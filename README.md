
# Identification of AI-Generated Academic Texts Using Watermarks

***WIP***

## Instructions

***WIP***

### Clone Repo

```shell
git clone https://github.com/ExoSkeletons/CS-F-WM.git
```

### Prerequisites

* Firebase Access
  * Place your `serviceAccountKey.json` in `/data`.
* OAuth Login
  * Place your `oauth_client.json` in `/data`.

### Configurations (Optional)
* Email Sending
  * Add the following to `config.yml` or in the Firestore config collection.
  ```json lines
  {
    email: {
      app_email: <Sender Email>
      app_password: <Sender Email App Password>
    }
  }
  ```

### Run

* **Survey App**
  * Launch Survey UI by running `survey.py`
* Watermarking Web Service
  * Webserver `/web/server.py`
  * Test Client `/web/client.py`
  * *For further detailed instructions, see `/web`*
