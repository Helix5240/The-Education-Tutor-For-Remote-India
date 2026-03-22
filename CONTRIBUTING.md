# Contributing to AI Tutor

First off, thank you for considering contributing to AI Tutor! It's people like you that make AI Tutor such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make one! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

## Fork & create a branch

If this is something you think you can fix, then fork AI Tutor and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```sh
git checkout -b 325-add-new-model
```

## Get the test suite running

Make sure you're using Python 3.9+ and have installed all requirements via `pip install -r requirements.txt`.

## Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first :smile:

## Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with AI Tutor's master branch:

```sh
git remote add upstream https://github.com/Helix5240/The-Education-Tutor-For-Remote-India.git
git checkout main
git pull upstream main
```

Then update your feature branch from your local copy of master, and push it!

```sh
git checkout 325-add-new-model
git rebase main
git push --set-upstream origin 325-add-new-model
```

Finally, go to GitHub and make a Pull Request!
