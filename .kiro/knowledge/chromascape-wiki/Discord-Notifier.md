The `DiscordNotification` class lets you send yourself messages in the event that your bot reaches a certain event. This can be useful for significant errors that make your bot stop, reaching an XP goal, reaching a GP goal and more.

## Discord setup:
You're going to need a Discord Webhook key and a Discord server to post updates to (takes less than 1 minute).
- Create a new server.
- Go to the server's settings.
- Navigate to integrations and subsequently Webhooks.
- Create a new Webhook, give it a name (if you want).
- Select the channel to broadcast to.
- Finally, hit "Copy Webhook URL".

## Setting up the secrets file:
Creating a secrets file is essential to keep your machine specific secret keys off Git and away from the public. If you have a public fork, without secrets -> everyone could ping your Discord Webhook.

- Create a `secrets.properties` file in the root directory of your project (this is the same level as src and the .gitignore file).
- Open it in an IDE or code editor of your choice.
- Add this property followed by your Webhook URL `discord.webhook.url=https://discord.com/api/webhooks/{webhook.id}/{webhook.token}`

> Ensure you paste in your own URL, not this example URL.

Then you're all done!