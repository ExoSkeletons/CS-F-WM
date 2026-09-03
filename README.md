
# Identification of AI-Generated Academic Texts Using Watermarks

WIP


### Prerequisites

* Firebase Access
  * Place `serviceAccountKey.json` in `/data`.
* OAuth Login
  * Place `oauth_client.json` in `/data`.
* Email Sending
  * Add
  ```
  {
    email: {
      app_email: <Sender Email>
      app_password: <Sender Email App Password>
    }
  }
  ```
  to `config.yml`, or in the Firestore config collection.