<div align="center">
  <img src="https://github.com/user-attachments/assets/c8a8ff17-791e-49e1-a7c6-9a0a37f16fd0" height="300" width="300">
</div>

# grabit

`grabit` is a command-line tool for recursively scanning a directory, extracting file contents, and saving or copying them to the clipboard while respecting `.grabit` rules. The tool helps turn complex projects into LLM input for big context questions.

## Development Note

I will endeavour to keep the docs on how to use `grabit` up to date, but time constraints mean they will likely slip behind as I ship features. The easiest way to see all the options available is to clone the repo run `grabit` on it and ask an LLM what's available! LOL. Or just read the source code if you know your Python.

## Features

- `grabit` is a pure Python CLI. No dependencies. So it works out of the box on Windows, macOS, and Linux.

### Scan

- Recursively extracts file contents from a directory.
- By default, includes git logs for the file to add extra context. This can be switched off with the flag `--no-git` or `-ng`. Turning off git significantly speeds up the process and reduces token count.
- Respects `.grabit` rules.
- Saves extracted content to a file or copies it to the clipboard.
- Prints a table of the files, with git information, and token sizes for files, with colour coding based on size in tokens.
- The table is orderable by the columns.

### bytes

- Recursively scans a directory and gets the size of all files in bytes.
- Very fast process, used to help you decide the regex you want to include or exclude. Fast iteration is the goal here.
- Prints out a table for the user to view, table can also be saved to file or copied to clipboard so you can paste into an LLM for advice.
- Colour coded byte sizes to help you understand the percentile differences in size.

### init

- Creates a default `.grabit` file with some standard regex and options set with some commentary on how to set up the file.

## Installation

Install `grabit` using pip:

```sh
pip install grabit
```

## Usage

### Initialise a `.grabit` file

```sh
grabit init
```

This will create a file in your current directory called `.grabit`.

### Scan a directory

This command is what you'll use to generate input for an LLM.

#### Standard

```sh
grabit scan /path/to/directory
```

The above command will output the LLM context to the terminal and ask you to use copy or output.

#### Copy output to clipboard

```sh
grabit scan /path/to/directory -c
```

#### Output to a file

```sh
grabit scan /path/to/directory -o some_output_file.txt
```

#### No git logs

```sh
grabit scan /path/to/directory -o some_output_file.txt -ng
```

#### Order output columns

Order by descending on the path.

```sh
grabit scan /path/to/directory --order path:desc
```

Order by ascending on the last modified by:

```sh
grabit scan /path/to/directory --order modified:asc
```

By default `asc` is used if you don't add anything, so

```sh
grabit scan /path/to/directory --order modified
```

Is the same as the above. If you want to see all possible options use:

```sh
grabit scan --help
```

### Bytes a directory

This command is what you'll use to quickly scan a directory and prepare your `.grabit` file for `scan`.

#### Copy output to clipboard

```sh
grabit bytes /path/to/directory -c
```

#### Output to a file

```sh
grabit bytes /path/to/directory -o some_output_file.txt
```

#### Order output columns

Order by descending on the path.

```sh
grabit bytes /path/to/directory --order path:desc
```

Order by ascending on the last modified by:

```sh
grabit scan /path/to/directory --order modified:asc
```

By default `asc` is used if you don't add anything, so

```sh
grabit scan /path/to/directory --order modified
```

Is the same as the above. If you want to see all possible options use:

```sh
grabit scan --help
```

### Print a directory tree

#### Print to terminal

```sh
grabit tree /path/to/directory
```

#### Print to clipboard

```sh
grabit tree /path/to/directory -c
```

#### Set the maximum depth

```sh
grabit tree /path/to/directory --depth 2
```

or

```sh
grabit tree /path/to/directory -d 2
```

## Ignore Files

Please do `grabit init` and read the commentary in the file to see how these work. They are currently (2025-03-04) in a state of constant change. Once they're more stable I will add a full tutorial.

## Example Output

When run, `grabit` will generate a structured output:

```
## `src/main.py`:
``
print("Hello, World!")
``

## `README.md`:
``
# Project Readme
``
```

## Versioning

Major.Minor.Patch

- Major: Breaking changes.
- Minor: New feature has been added, but it is backwards compatible.
- Patch: Backwards compatible bug fixes or small doc changes.

## Future Features

- [ ] include ~~and exclude~~ sections in `.grabit`.
- [ ] different titled configurations in the `.grabit` file. i.e. you could have a configuration for getting section A of your app, and another for section B of your app to make it easier to set the configs once and not worry afterwards.
- [ ] add a command line argument option for adding an include or an exclude regex, something like grabit -e "some-regex" or grabit -i "some-regex".
- [ ] include a directory tree in the output as well as the code.
- [x] ~~tell the user the rough number of tokens that have been found across all the files.~~
- [x] ~~predict the number of tokens in a file based on the number of characters in each file.~~
- [ ] if the number of tokens is high, intelligently group files by suffix and prefix and ask the user if they'd like to include or exclude them.
- [x] ~~ask the user if they'd like to include only a snippet of parts of long files, i.e. first 50 lines or so. Allow them to set this on a per file basis.~~
- [x] ~~add sensible defaults to the `.grabit` file produced by `grabit init`.~~
- [ ] automatically generate or update the `.grabit` file to reflect the user's choices in the above two features.
- [ ] ask the user if they want to include large directories as well, not just by prefix.
- [ ] add an option for setting up a query on the cli that helps grabit decide how simliar files are to that query and suggest including or discluding based on that. Cursor do something like this, a vector database.
- [ ] store the query inside of the `.grabit` file for faster query re-runs.
- [x] ~~if the files have git history, find the git history of every collected file and add when it was last changed.~~
- [x] ~~taking the above further, optionally add the entire git log of commits for each file, or the last N commits or what have you. This could add extra context for an LLM.~~
- [ ] add an option to include the git diff of each file, or the last N diffs or what have you. This could add even more context for an LLM, an optional argument could be add that switches this on.
- [x] ~~add the ablity to collect the whole git history of the repo, all the logs.~~
- [ ] get a log timeline, so you can see how much activity each file has in git. This extra information could be used to help decide which files to include or exclude. It could also help the user decide how important a particular file is. Especially if data on recent history is provided.
- [ ] add tests to the package to avoid changes causing failure.
- [x] ~~decide on versioning strategy and add to `README.md`~~
- [ ] add standard configuration setting for `.grabit` files. This will run through their directory and make decisions for them, outputting choices to the terminal for the user to review. e.g. skipping extra large files, or skipping known auto-genned file types like `.dll`.
- [ ] add a terminal based configuration building process that guides users through the various `.grabit` options and lets them build their `.grabit` file via the terminal
- [ ] add an option to set the target number of tokens that grabit should not go over. Then when grabit does go over it will make suggestions underneath the table on what you could do to lower the amount of tokens. If there are embeddings as well, this could be very helpful for figuring out how important different directory paths etc. are.
- [x] ~~build directory path trees whilst collecting so that more than just the path name can be used to group the directories and find similarities that could be exploited for removing tokens.~~
- [x] ~~colour the output that's given to the user depending on size so it's easier to see patterns and make decisions on what to include or disclude.~~
- [ ] potentially colour the file endings of different file types to also add a visual cue to the user.
- [x] ~~add an option to order table output by token sizes, last modified by, by order scanned, by file path, and by date last modified.~~
- [x] ~~add an option for quickly scanning through a directory and getting sizes in bytes very quickly to make choice on inclusion faster.~~
- [x] ~~improve the option for fast search to include colour coding and ordering by column.~~
- [ ] update the `bytes` command so that the file endings also have their total bytes colour coded.
- [ ] use the `curses` built in python package to make a terminal app for automated actions: https://docs.python.org/3/howto/curses.html
- [ ] add a different kind of file type than `.grabit` or extend the `.grabit` file type to allow formatted messages. i.e. you should be able to write prompts that rely on `grabit` commands. So in the `.grabit` file you would set up several different configs, then in the prompt creation file you would use `<!grabit config some-config?>` or something along these lines. This would make it possible to build prompts quickly and only build them once, in such a way that you can set up repeat questions very effectively, or re-use prompt structure easily. It would also allow for `grabit` to ship with some basic configs already set up.
- [ ] add a global set of include and exclude under a header like `# global` or something, this would apply everywhere across all configs.
- [x] ~~add a command to print a directory tree, just like the `tree` command in Linux but prettier~~.

## License

MIT License

[Connor Skelland](https://github.com/Connor56)
