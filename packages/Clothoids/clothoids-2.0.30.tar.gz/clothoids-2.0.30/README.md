# Clothoids

Fork of [Clothoids](https://github.com/ebertolazzi/Clothoids) by Enrico Bertolazzi.

This is just a fork that tries its best to keep stable releases and stay up-to-date.

Unless it relates directly to something here (e.g., a broken release) please refer to the original repo!

## Installation

In each release you can find precompiled binaries for Windows, Linux and MacOS. You can also compile the library yourself, but first you need to install the dependencies:

- ruby >=2.6 with the following gems: rake, colorize, rubyzip;
- CMake with ninja;
- python 3.8-13 (other versions are untested).

Once those requirements are installed, simply:

```bash
git clone --branch stable --depth 1 https://github.com/SebastianoTaddei/Clothoids.git
cd Clothoids
ruby setup.rb
rake
```

Python bindings are also available, for those see the `src_py/README.md`.
