---
icon: lucide/monitor-up
---

# Deploy your app

Now that you've built your first RAG application, let's deploy it.

## Local deployment

Run your app locally:

```console
$ toolfront serve my-app --port 8000
```
> Runs on `http://127.0.0.1:8000`

## Cloud deployment

Create a free [Statespace account](#cloud-deployment)[^1] and deploy your app to the cloud:

```console
$ toolfront deploy my-app --api-key <your-statespace-key>
```
> Deploys to `https://your-app.toolfront.app`

## Test your deployment

Open the application URL in your browser. You should see your `README.md`.

---

!!! success
    Your app is now running locally or in the cloud.

    **Next:** [Connect AI agents](interact.md)

[^1]: Statespace is currently in beta. Email `esteban[at]statespace[dot]com` or join our [Discord](https://discord.gg/rRyM7zkZTf) to get an API key