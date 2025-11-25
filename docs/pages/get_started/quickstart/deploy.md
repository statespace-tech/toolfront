---
icon: lucide/monitor-up
---

# Deploy Your App

Now that you've built your status checker, let's deploy it.

## Local Deployment

Run your app locally:

```bash
toolfront serve my-app --port 8000
```
> Your app will be running on `http://127.0.0.1:8000`

## Cloud Deployment

Create a free [Statespace account](#cloud-deployment)[^1] and get an API key. Then, deploy to ToolFront Cloud:

```bash
toolfront deploy my-app  --api-key <your-statespace-key>
```
> Your app will be deployed to `https://<app_id>.toolfront.app`


## Test Your Deployment

Open the application URL in your browser. You should see the `README.md` content.

---

!!! success
    Your app is now running locally or in the cloud.

    **Next:** [Connect AI agents](interact.md)

[^1]: Statespace is currently in beta. Email `esteban[at]statespace[dot]com` or join our [Discord](https://discord.gg/rRyM7zkZTf) to get an API key