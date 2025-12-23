# FileDrop

A simple file upload and download web application built with **Flask**. It supports both **local storage** for development and **AWS S3 + DynamoDB** for deployment.

---

## Features

- Upload files
- Download files from generated link
- Set expiration Time
- Optional Password

---

## TODO
- Password Attempts
- Better visual for error pages
---

## Running with AWS
- use `python app.py --no-use-local` to configurate the app to use DynamoDB and S3

