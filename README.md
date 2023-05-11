![Build Website](https://github.com/mcmikecreations/tum_info/actions/workflows/jekyll-gh-pages.yml/badge.svg)

A bunch of useful information I've collected while studying at the Technical University of Munich.

The contributors imagined/came up with all of the course information in this repo randomly, including the grades.
All matches with real courses and grades are purely coincidental.

## How to contribute

### Course exam statistics

You can help expand this website with new information by adding your own course exam statistics!

#### All your courses program

If you're looking for a simple way to send me your grades, you can contribute using the executable file ([Windows](https://github.com/mcmikecreations/tum_info/releases/download/0.9.0/Grades.exe), [Linux](https://github.com/mcmikecreations/tum_info/releases/download/0.9.0/Grades), [MacOS](https://github.com/mcmikecreations/tum_info/releases/download/0.9.0/Grades.dmg)). You'll find a video guide [here](https://youtu.be/nHjuVhIJRaQ). Now you can generate a file with all your grades and send it over Telegram or any other of the communication channels listed in the app!

**For developers**: to build the app, you need `python>=3.7` and install `BeautifulSoup4 requests PySide6 pyinstaller` through `pip`. You can test-run the app running `python scripts/course_glob_ui.py` from root folder. To build it, run `pyinstaller scripts/course_glob_ui.spec`, the results will be placed in the `dist` folder. To package for MacOS, you need to have an additional utility installed through `brew install create-dmg`. Then run `./scripts/course_glob_ui_build.sh` from root folder.

#### Grade download script

A handy script was created to extract all grade reports for a TUMOnline student account. To run the script:

1. Install git, add it to PATH.
2. Fork the repository, clone your fork.
3. Install Python 3.7 or newer, add python and pip to PATH.
4. Run `pip install requests`.
5. From repository root run `python scripts/course_glob.py name=ab12cde@mytum.de pass=42424242`.
6. If you get errors, report them by creating a new issue.
7. Check endterm/retake filenames and field in files. Check exam_type, mode, lang fields in files.
8. Commit changes, push to your fork, create a pull request.

#### Single course

In short, create a new issue based on this template by [going here](https://github.com/mcmikecreations/tum_info/issues/new?assignees=&labels=&template=add_course_exam_statistics.md&title=%5BCourse%5D+CIT+IN0001+2022SS) and replace the values with your own data.
The description is copy-pasted onto the page directly and follows the markdown format (but you can use plain text too).
After some time, the statistics you have submitted will appear on the website.
For now there's a manual review step done by me, so don't worry too much about breaking the website.
When I see that everything is ok, I put a label on the issue and [GitHub Actions](https://github.com/mcmikecreations/tum_info/tree/main/.github/workflows)
take care of the rest by adding a new page to the website and building it.

### Feature requests and bug reports

There also are issue templates for such cases [back on GitHub](https://github.com/mcmikecreations/tum_info/issues/new/choose).
If something is wrong or you want something to get better, here's what to do:
1. Create a new issue and outline what is wrong and/or what you need.
2. (Optionally) If you want to try and fix the issue, state it in a comment, fork the repo, make the changes, and submit a pull request.
