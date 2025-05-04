# gomi

[![Chat](https://img.shields.io/badge/chat-join-green.svg)](https://tatsumoto-ren.github.io/blog/join-our-community.html)
[![Channel](https://shields.io/badge/channel-subscribe-blue?logo=telegram&color=3faee8)](https://t.me/ajatt_tools)
[![Donate](https://img.shields.io/badge/patreon-support-orange)](https://tatsumoto.neocities.org/blog/donating-to-tatsumoto)

Gomi is a Python package used to store and manage Note Types for Anki in a git repository.
At Ajatt-Tools, we store our note types [here](https://github.com/Ajatt-Tools/AnkiNoteTypes).
Gomi provides a super user-friendly mechanism of importing and exporting note types,
and everyone is welcome to add their templates to our collection by making a pull request.

## Prerequisites

### GNU/Linux

Install [Python](https://wiki.archlinux.org/title/Python) 3.12 or later if you haven't already.

### Windows

Windows is not recommended [because it is malware](https://www.gnu.org/proprietary/malware-microsoft.html).

<details>

Install Python from the Microsoft Store or check if you already have the good version
putting on your file explorer search bar

````
%LOCALAPPDATA%\Microsoft\WindowsApps\python3
````

If you have the correct version, you can just close the python's window that just popped up.

Make sure to add python3 to the `PATH`.
The path you need to add should look like `C:\Users\[YourUsername]\AppData\Local\Microsoft\WindowsApps\python3`.

If you don't have the python installed,
when you'll put this command into the search bar,
it will open a microsoft store window directly on the correct python version,
and you just need to click Download.

After doing this step, you can make sure that everything is good
by opening the command prompt with `Windows+R`, `cmd` and put the command:

```
python3 -m
```

If everything's good, you should get a response like : `Argument expected for the -m option`

</details>

## Installation

Install [gomi](https://pypi.org/project/gomi/) using [pipx](https://pipx.pypa.io/): `pipx install gomi`.

## Usage

Make sure Anki is running, and you have
[AnkiConnect](https://ankiweb.net/shared/info/2055492159)
installed.

Clone [AnkiNoteTypes](https://github.com/Ajatt-Tools/AnkiNoteTypes) and `cd` into it.
If you have never cloned a repository before,
you need to install [git](https://git-scm.com/).
If you have `git` installed,
open your terminal and type the following commands.

```
git clone "https://github.com/Ajatt-Tools/AnkiNoteTypes.git"
cd AnkiNoteTypes
```

### Importing

To import one of the
[available Note Types](https://github.com/Ajatt-Tools/AnkiNoteTypes/tree/main/templates)
to Anki, run:

```
gomi import
```

**Note:** When using [AJT Japanese](https://tatsumoto.neocities.org/blog/anki-japanese-support.html),
reopen the current profile to add the add-on's scripts to the note type after importing and after updating.
Alternatively, open AJT Japanese's settings and press "Ok" ("Accept").

### Updating

If you imported a note type from the AJATT collection before,
it received an update,
and you want to import the new version, run:

```
gomi update
```

### Exporting

To export one of your Note Types, run:

```
gomi export
```

Then write a helpful readme and commit your changes:

```
git add templates media && git commit
```

After committing your template, please [create a pull request](https://github.com/Ajatt-Tools/AnkiNoteTypes/pulls).

## Caveats

Although `gomi` supports note types that reference external `CSS` and `JS` files
stored in the `collection.media` folder,
for example,
by using `<script src="_script.js"></script>` in a Front or Back template,
or by using `@import url("_styling.css");` in the Styling section,
there are a few caveats to keep in mind.

* The filenames should begin with an underscore to prevent Anki from flagging them as unused.
* If you use _AnkiWeb_ to sync your collection with other devices (like an Android phone),
  external files will only sync once.
  If you change your externally linked `CSS` or `JS` file,
  you'll need to rename it so that updates are sent to your other devices.
  However, referencing external fonts is acceptable because they typically need to be synced only once.
* Specifically, loading external `JS` files
  [causes a slight flicker or lag](https://forums.ankiweb.net/t/flickering-issue-caused-by-js/47065)
  whenever you flip a card.
  It is recommended that you use inline scripts instead:

  ```html
  <script>
  // some code
  </script>
  ```
