/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

// This has been deprecated in favor of `pyrefly init`.
// The very basic version of this script takes the path to the config file
// as an argument, reads it, parses it, converts it, and writes it out.
// Future features:
// - match up the error configurations (best-effort)
// This script does not otherwise invoke pyrefly. This gives the user time to change anything by hand if needed.

use std::path::Path;
use std::path::PathBuf;

use anyhow::Context as _;
use clap::Parser;
use tracing::error;
use tracing::info;

use crate::commands::run::CommandExitStatus;
use crate::config::config::ConfigFile;
use crate::config::mypy;
use crate::config::mypy::MypyConfig;
use crate::config::pyright;
use crate::config::pyright::PyrightConfig;
use crate::config::util::PyProject;
use crate::util::fs_anyhow;
use crate::util::upward_search::UpwardSearch;

#[derive(Clone, Debug, Parser)]
pub struct Args {
    /// The path to the mypy or pyright config file to convert. Optional.
    /// If not provided, or if it's a directory, pyrefly will search upwards for a
    /// mypy.ini, pyrightconfig.json, or pyproject.toml.
    pub input_path: Option<PathBuf>,
    /// Optional path to write the converted pyre.toml config file to. If not provided, the config will be written to the same directory as the input file.
    pub output_path: Option<PathBuf>,
}

impl Args {
    fn load_from_pyproject(raw_file: &str) -> anyhow::Result<ConfigFile> {
        info!("Attempting to load [tool.mypy] config");
        match mypy::parse_pyrproject_config(raw_file) {
            ok @ Ok(_) => {
                info!("Successfully loaded [tool.mypy] config from pyproject.toml");
                return ok;
            }
            Err(e) => {
                info!("Failed to load [tool.mypy] config from pyproject.toml:\n  {e}");
                info!("Attempting to load [tool.pyright] config.");
            }
        }
        pyright::parse_pyproject_toml(raw_file)
            .inspect(|_| info!("Successfully loaded [tool.pyright] config from pyproject.toml"))
            .inspect_err(|e| {
                info!("failed to load [tool.pyright] config from pyproject.toml:\n  {e}")
            })
    }

    fn find_config(start: &Path) -> anyhow::Result<PathBuf> {
        let searcher = UpwardSearch::new(
            // Search for pyproject.toml last, because we're only going to find 1 config.
            vec![
                "mypy.ini".into(),
                "pyrightconfig.json".into(),
                "pyproject.toml".into(),
            ],
            |p| std::sync::Arc::new(p.to_path_buf()),
        );
        searcher.directory(start).map_or_else(
            || Err(anyhow::anyhow!("Failed to find config")),
            |p| Ok(std::sync::Arc::unwrap_or_clone(p)),
        )
    }

    pub fn run(&self) -> anyhow::Result<CommandExitStatus> {
        if let Some(path) = self.input_path.as_ref() {
            if !path.exists() {
                error!("Could not find or cannot access `{}`", path.display());
                return Ok(CommandExitStatus::InfraError);
            }
        }
        let input_path = match &self.input_path {
            Some(path) if path.is_file() => {
                info!("Looking for {}", path.display());
                path
            }
            Some(path) => {
                info!("Looking for configs to migrate in {}", path.display());
                &Self::find_config(path)?
            }
            None => {
                let cwd = std::env::current_dir()
                    .context("Could not find dir to start search for configs from")?;
                info!(
                    "No config path provided. Searching for configs, starting in {}",
                    cwd.display()
                );
                &Self::find_config(&cwd)?
            }
        };
        let config = if input_path.file_name() == Some("pyrightconfig.json".as_ref()) {
            let raw_file = fs_anyhow::read_to_string(input_path)?;
            info!("Detected pyright config file");
            let pyr = serde_json::from_str::<PyrightConfig>(&raw_file)?;
            pyr.convert()
        } else if input_path.file_name() == Some("mypy.ini".as_ref()) {
            info!("Detected mypy config file");
            MypyConfig::parse_mypy_config(input_path)?
        } else if input_path.file_name() == Some("pyproject.toml".as_ref()) {
            let raw_file = fs_anyhow::read_to_string(input_path)?;
            info!("Detected pyproject.toml file.");
            Self::load_from_pyproject(&raw_file)?
        } else {
            error!(
                "Currently only migration from pyrightconfig.json, mypy.ini, and pyproject.toml is supported, not {}",
                input_path.display(),
            );
            return Ok(CommandExitStatus::UserError);
        };
        info!("Conversion finished");

        let output_path = match &self.output_path {
            Some(path) => path,
            None => {
                if input_path.ends_with(ConfigFile::PYPROJECT_FILE_NAME) {
                    input_path
                } else {
                    &input_path.with_file_name(ConfigFile::PYREFLY_FILE_NAME)
                }
            }
        };
        if output_path.ends_with(ConfigFile::PYPROJECT_FILE_NAME) {
            write_pyproject(output_path, config)?;
            info!("Config written to {}", output_path.display());
        } else {
            let serialized = toml::to_string_pretty(&config)?;
            fs_anyhow::write(output_path, serialized.as_bytes())?;
            info!("New config written to {}", output_path.display());
        }
        Ok(CommandExitStatus::Success)
    }
}

pub fn write_pyproject(pyproject_path: &Path, config: ConfigFile) -> anyhow::Result<()> {
    // TODO: Use toml_edit to replace the existing tool.pyrefly config, if one exists.
    // This merely appends the new config to the end of the file.
    let config = PyProject::new(config);
    let serialized = toml::to_string_pretty(&config)?;
    fs_anyhow::append(pyproject_path, serialized.as_bytes())
        .with_context(|| "While trying to write the pyrefly config to the pyproject.toml file")
}

#[cfg(test)]
mod tests {
    use serde::Deserialize;

    use super::*;
    use crate::util::globs::Globs;

    #[test]
    fn test_run_pyright() -> anyhow::Result<()> {
        let tmp = tempfile::tempdir()?;
        let input_path = tmp.path().join("pyrightconfig.json");
        let pyr = br#"{
    "include": ["src/**/*.py"]
}
"#;
        fs_anyhow::write(&input_path, pyr)?;
        let output_path = input_path.with_file_name(ConfigFile::PYREFLY_FILE_NAME);

        let args = Args {
            input_path: Some(input_path),
            output_path: None,
        };
        let status = args.run()?;

        assert!(matches!(status, CommandExitStatus::Success));
        let output = fs_anyhow::read_to_string(&output_path)?;
        // We're not going to check the whole output because most of it will be default values, which may change.
        // We only actually care about the includes.
        let output_lines = output.lines().collect::<Vec<_>>();
        assert_eq!(output_lines[0], r#"project_includes = ["src/**/*.py"]"#);
        assert!(output_lines.len() > 1);
        ConfigFile::from_file(&output_path, false)?;
        Ok(())
    }

    #[test]
    fn test_run_mypy() -> anyhow::Result<()> {
        let tmp = tempfile::tempdir()?;
        let input_path = tmp.path().join("mypy.ini");
        let output_path = input_path.with_file_name(ConfigFile::PYREFLY_FILE_NAME);
        // This config is derived from the pytorch mypy.ini.
        let mypy = br#"[mypy]
files =
    src,
    other_src,
    test/some_test.py,

mypy_path = some_paths:comma,separated

unknown_option = True

exclude = src/include/|other_src/include/|src/specific/bad/file.py

[mypy-some.*.project]
ignore_missing_imports = True

[mypy-some.specific.project.subdir]
ignore_missing_imports = True

[mypy-stricter.on.this.*]
check_untyped_defs = True
"#;
        fs_anyhow::write(&input_path, mypy)?;

        let args = Args {
            input_path: Some(input_path),
            output_path: None,
        };
        let status = args.run()?;
        assert!(matches!(status, CommandExitStatus::Success));

        // We care about the config getting serialized in a way that can be checked-in to a repo,
        // i.e. without absolutized paths. So we need to check the raw file.
        #[derive(Deserialize)]
        struct CheckConfig {
            project_includes: Vec<String>,
            search_path: Vec<String>,
        }
        let raw_output = fs_anyhow::read_to_string(&output_path)?;
        let CheckConfig {
            project_includes,
            search_path,
        } = toml::from_str::<CheckConfig>(&raw_output)?;
        assert_eq!(
            project_includes,
            vec!["src", "other_src", "test/some_test.py"]
        );
        assert_eq!(search_path, vec!["some_paths", "comma", "separated"]);
        Ok(())
    }

    #[test]
    fn test_run_pyproject_mypy() -> anyhow::Result<()> {
        let tmp = tempfile::tempdir()?;
        let input_path = tmp.path().join("pyproject.toml");
        let pyproject = br#"[tool.mypy]
files = ["a.py"]
"#;
        fs_anyhow::write(&input_path, pyproject)?;
        let args = Args {
            input_path: Some(input_path),
            output_path: None,
        };
        let status = args.run()?;
        assert!(matches!(status, CommandExitStatus::Success));
        let input_path = args.input_path.unwrap();
        let pyproject = fs_anyhow::read_to_string(&input_path)?;
        assert_eq!(pyproject.lines().next().unwrap(), "[tool.mypy]");
        assert!(pyproject.contains("[tool.pyrefly]"));
        Ok(())
    }

    #[test]
    fn test_run_pyproject_pyright() -> anyhow::Result<()> {
        let tmp = tempfile::tempdir()?;
        let input_path = tmp.path().join("pyproject.toml");
        let pyproject = br#"[tool.pyright]
include = ["a.py"]
"#;
        fs_anyhow::write(&input_path, pyproject)?;
        let args = Args {
            input_path: Some(input_path),
            output_path: None,
        };
        let status = args.run()?;
        assert!(matches!(status, CommandExitStatus::Success));
        let input_path = args.input_path.unwrap();
        let pyproject = fs_anyhow::read_to_string(&input_path)?;
        assert_eq!(pyproject.lines().next().unwrap(), "[tool.pyright]");
        assert!(pyproject.contains("[tool.pyrefly]"));
        assert!(!tmp.path().join("pyrefly.toml").exists());
        Ok(())
    }

    #[test]
    fn test_run_pyproject_bad_mypy_into_pyright() -> anyhow::Result<()> {
        let tmp = tempfile::tempdir()?;
        let input_path = tmp.path().join("pyproject.toml");
        let pyproject = br#"[tool.pyright]
include = ["a.py"]

[tool.mypy]
files = 1
"#;
        fs_anyhow::write(&input_path, pyproject)?;
        let args = Args {
            input_path: Some(input_path),
            output_path: None,
        };
        let status = args.run()?;
        assert!(matches!(status, CommandExitStatus::Success));
        Ok(())
    }

    #[test]
    fn test_run_pyproject_mypy_over_pyright() -> anyhow::Result<()> {
        // The current implementation favors mypy over pyright. This test documents that.
        // However, we may want to change this in the future, so it's OK to break this test.
        let pyproject = r#"[tool.pyright]
include = ["pyright.py"]

[tool.mypy]
files = ["mypy.py"]
"#;
        let cfg = Args::load_from_pyproject(pyproject)?;
        assert_eq!(cfg.project_includes, Globs::new(vec!["mypy.py".to_owned()]));
        Ok(())
    }

    #[test]
    fn test_find_config_find_mypy() -> anyhow::Result<()> {
        let tmp = tempfile::tempdir()?;
        let bottom = tmp.path().join("a/b/c/");
        std::fs::create_dir_all(&bottom)?;
        fs_anyhow::write(&tmp.path().join("a/mypy.ini"), b"[mypy]\n")?;
        fs_anyhow::write(&tmp.path().join("a/pyproject.toml"), b"")?;
        let found = Args::find_config(&bottom)?;
        assert!(found.ends_with("mypy.ini"));
        Ok(())
    }

    #[test]
    fn test_find_config_find_from_dir() -> anyhow::Result<()> {
        let tmp = tempfile::tempdir()?;
        let bottom = tmp.path().join("a/b/c/");
        std::fs::create_dir_all(&bottom)?;
        fs_anyhow::write(&tmp.path().join("a/mypy.ini"), b"[mypy]\n")?;
        let status = Args {
            input_path: Some(bottom),
            output_path: None,
        }
        .run()?;
        assert!(matches!(status, CommandExitStatus::Success));
        assert!(tmp.path().join("a/pyrefly.toml").try_exists()?);
        Ok(())
    }

    #[test]
    fn test_existing_file_to_new_pyproject() -> anyhow::Result<()> {
        let tmp = tempfile::tempdir()?;
        let input_path = tmp.path().join("pyrightconfig.json");
        let pyr = br#"{
    "include": ["src/**/*.py"]
}
"#;
        fs_anyhow::write(&input_path, pyr)?;
        let output_path = input_path.with_file_name(ConfigFile::PYPROJECT_FILE_NAME);

        let args = Args {
            input_path: Some(input_path),
            output_path: Some(output_path.clone()),
        };
        let status = args.run()?;

        assert!(matches!(status, CommandExitStatus::Success));
        let output = fs_anyhow::read_to_string(&output_path)?;
        assert!(output.contains("[tool.pyrefly]"));
        assert!(output.contains(r#"src/**/*.py"#));
        assert!(!tmp.path().join("pyrefly.toml").exists());
        Ok(())
    }

    /*
    #[ignore = "Cannot edit toml files in a way that preserves order and comments"]
    #[test]
    fn test_overwrite_existing_toolpyrefly() -> anyhow::Result<()> {
        let tmp = tempfile::tempdir()?;
        let input_path = tmp.path().join("pyrightconfig.json");
        fs_anyhow::write(&input_path, b"{}")?;
        let output_path = tmp.path().join("pyproject.toml");
        fs_anyhow::write(
            &output_path,
            br#"[project]
name = "test"

[tool.a]
test = true

[tool.z]
test = true

# I'm a comment!

[tool.pyrefly]
incomplete = true

[tool.b]
test = true
"#,
        )?;
        let args = Args {
            input_path: Some(input_path),
            output_path: Some(output_path.clone()),
        };
        let status = args.run()?;
        assert!(matches!(status, CommandExitStatus::Success));

        let output = fs_anyhow::read_to_string(&output_path)?;
        let headers = output
            .lines()
            .filter(|l| l.starts_with(['[', '#']))
            .collect::<Vec<_>>();
        assert_eq!(
            headers,
            vec![
                "[project]",
                "[tool.a]",
                "[tool.z]",
                "# I'm a comment!",
                "[tool.pyrefly]",
                "[tool.b]",
            ]
        );

        let config = toml::from_str::<toml::Table>(&output)?;
        assert!(
            !config["tool"]["pyrefly"]
                .as_table()
                .is_some_and(|table| table.contains_key("incomplete"))
        );

        Ok(())
    }
    */
}
