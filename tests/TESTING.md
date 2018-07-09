# Testing Documentation

### Testing a PR Locally 

1. Make note of the PR number. For example, Rod's latest is PR #99: https://github.com/DedSecInside/TorBot/pull/99

2. Fetch the PR's pseudo-branch, and give it a local branch name. Here we'll name it `pr99`:
  ```
  $ git fetch origin pull/99/head:pr99
  ```

3. Switch to that branch:
  ```
  $ git checkout pr99
  ```

4. Compile and test.

If the PR code changes and you want to update:

```
# Do this while in the pr99 branch
$ git pull origin pull/99/head
```

(I try to avoid `pull` and instead use `fetch`+`merge`, but... I don't know how to do it for this.)

### Merging the PR

You can use the Github web interface, but there's a [TOCTOU](https://en.wikipedia.org/wiki/Time_of_check_to_time_of_use) problem: If the pull-requester changes their master (or whatever they're PRing from) between the time you test and the time you merge, then you'll be merging code that you haven't reviewed/tested. So let's do it on the command line.

First, checkout the upstream master code:

You'll only do this the first time -- it creates the local `new_master` branch, tracks it to `new_master`, and switches to the branch:
```
$ git checkout -t -b new_master origin/master
```

After the first time you'll just do:
```
$ git checkout new_master
```

Now merge the PR:
```
$ git merge pr99
```

NOTE: You should edit the merge commit message to reference the PR (using, say `#99` in it).

Now push:
```
$ git push origin HEAD:master
```

(You can't just `git push` because your local branch name is different than the remote.)
