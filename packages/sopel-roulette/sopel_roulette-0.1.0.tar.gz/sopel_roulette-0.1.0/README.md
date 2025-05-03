# sopel-roulette

Sopel plugin clone of a mIRC script to let users play Russian roulette

## Installing

Releases are hosted on PyPI, so after installing Sopel, all you need is `pip`:

```shell
$ pip install sopel-roulette
```

### Requirements

None aside from Sopel itself, version 8 or higher. (This implies a minimum
Python version of 3.8.)

## Configuring

The easiest way to configure `sopel-roulette` is via Sopel's configuration
wizard—simply run `sopel-plugins configure roulette` and enter the values for
which it prompts you.

### Available options

* `timeout`: How long in seconds each user must wait between games

## Using

* `.roulette`: Performs a game of Russian roulette, prints the result to the
  channel, and updates the user's stats
* `.r [nickname]`: Retrieves and displays stats for the calling user, or (when
  `nickname` is specified) the specified nick.
