# Tweetmetric

Tweetmetric allows you to track various metrics on your most recent tweets, such as impressions, retweets and clicks on your profile.

![example image](./img/dashboard.png)

The code is in Python, and the frontend uses Dash (a Plotly web interface). Tweetmetric uses Redis  as a fast database

## Getting started

Install `docker` and `docker-compose`.

If you're on windows or mac, you can use [Docker Desktop](https://www.docker.com/products/docker-desktop), you'll have to replace all the `docker-compose` command by `docker compose`.

Tweetmetric uses private metrics that can only be accessed by the Tweet's owner. You need to provide your API keys to the program so it can work.
- Request a Twitter API key on [The Twitter developer portal](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api). This only takes a couple minutes, you need to have a verified phone number on your account.
- Generate a user token for the app you just created on [the developer dashboard](https://developer.twitter.com/en/portal/dashboard)
- You should now have 4 secrets provided by Twitter. Store them in their corresponding strings inside a `.env` file (you can create it from the [`.env.dist`](./.env.dist) example)

```shell
$ cp .env.dist .env
# replace all the variables in the .env file
$ docker-compose up -d
```

And that's it.

## Contributions

If you have to add a python dependancies in order to patch or add some features, please complete the [requirements.txt](./src/requirements.txt).

If you need to rebuild the images because you made some changes:

```shell
$ docker-compose up -d --build
```
