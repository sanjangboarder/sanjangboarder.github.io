---
title: "Building an Algorithmic Stock Trading System as an Embedded Dev and Stock Novice - Part 1: Environment Setup"
date: 2026-09-15
category: "IT, Software & Drones"
categoryNo: 33
logNo: 224412358072
source: "https://m.blog.naver.com/sanjangboarder/224412358072"
thumbnail: "https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTNfMTE2/MDAxNzg5MzA0NjEzNzg4.wP2s9ukg2m3WA_dMg-5leBqGzXMK51vvUthic2tL-AMg.UsTECEfu7RvBTfNMtDCI5elaFRsT7Rro_WAycWreqDIg.PNG/image.png"
description: "Embedded software engineer and stock novice shares how to set up a 24/7 algorithmic trading system using AWS Lightsail, GitHub CI/CD, agy CLI, and Telegram."
lang: "en"
---

Hello, this is SanjangBorder.

​

I belong to a private investment study group named PlatformK. Until now, I simply entrusted a set amount of funds to CEO Kim for management, but to help members overcome our financial and economic ignorance, CEO Kim recently gave the PlatformK members a specific challenge.

​

I thought, "How hard could it be?" and agreed to try it out... For context, although I have been working as an embedded software engineer for 20 years, I was virtually clueless when it came to web development and the stock market. With this opportunity, I decided to take on the challenge by leveraging AI. It has now been about a week since I started, and after experiencing various hurdles and trial-and-error, solid architectural concepts have started taking shape, so I want to share them one by one.

​

**First Assignment Title**

​

> Build an automated algorithmic trading program implementing the Grid Strategy.
>
> Must execute through a Korea Investment & Securities account.
>
> PlatformK CEO Kim

​

Receiving the assignment made my mind race. While I planned to build it using AI, developing it on my home desktop PC would certainly let me hack it together quickly—but keeping it solely on a home PC would severely restrict when and where I could work on it. I started pondering an environment setup that could run non-stop 24/7 and allow continuous development anytime, anywhere, even from a smartphone. After a day of searching and discussing with AI, I arrived at a clear conclusion.

​

Here are the essential requirements I identified for the software development and operating environment, and how I built them.

​

**Systematic Program Management Through GitHub**

​

To maintain code history, enable rollbacks at any moment, and guarantee stable service operation, I created a Git repository and built a CI pipeline. I set up a private GitHub repository and configured automated pipelines using GitHub Actions.

​

![](https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTNfMTY1/MDAxNzg5MzA0MzQxNzQ4.1gpEAUaiO1qyGLc1PtUtOKGlr346RtIiT8uy8aikXAgg.sMtV63nVSlLDXiXoM2FlZhMsDRoOG-RFMB1MdXjJ7ysg.PNG/image.png?type=w800)

​

Using GitHub makes source code sharing straightforward and enables effortless project management. For non-traditional developers building software with AI, the importance of software configuration management (version control) might not seem immediately obvious, but letting AI handle repository maintenance makes it so easy that everyone should give it a try.

​

![](https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTNfNzcg/MDAxNzg5MzA0NjYyNDIy.6-NZVDO9_e2ZCXjUirl6Uz3U6o4yMJEyd9LDeAJyFOsg.214Y31NvWwM1_ZuhR8Hx5mqlz7jQzm43a4KCf5Y8798g.PNG/image.png?type=w800)
![](https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTNfMjgz/MDAxNzg5MzA1NTQyNzM1.KkK2c1C_s6sNL1RtqC-U76daSTd1Tx2tSGqaIfZ5Oekg.QE1tK9E8uEeVnXEesG9dq2OB7kHmgZwdKIuZbmt88IMg.PNG/image.png?type=w800)

​

****

​

---

​

**Configuring a Free 24/7 Server Environment**

​

Automated algorithmic trading cannot just cater to regular Korean domestic market hours; it must support after-hours sessions and US stock market trading, making continuous, uninterrupted 24/7 service essential. I initially considered dedicated low-power mini PCs or a Mac mini, but recent hardware prices have climbed significantly. Searching for ways to keep overhead low, the service I discovered was Amazon Lightsail. I chose the $12/month instance tier. Since AWS provides $200 in free credits, strategic usage allows you to operate the server for nearly two years completely free of charge.

​

![](https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTNfMTMx/MDAxNzg5MzA0NzU0NTM1.nEhDX1Okc-IgFuFcnuxZ1mi4DLmSy9nxit6iHN02zvQg.WLCeSkxtQBllcUh2HljRJekAPIGQYQ_mfYn0ltmAyuwg.PNG/SE-8e39fcd8-0f54-40ac-b759-a02f08a47b08.png?type=w800)

​

Please see below for the remote architecture and development environment setup.

​

![](https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTNfMTM4/MDAxNzg5MzA0NzgyNjk2.ug6cq-rFRIJJVpAA9wlDNCmGZQH9nQpCbv29oRxldRkg.t1k5_YhNb0Tq2snqrmPdjC8CnZ51Q4nUi-8OvWRehoMg.PNG/SE-dc8de2b2-1d34-4968-a589-2442d0335533.png?type=w800)

​

To inspect algorithmic trading statuses through a web dashboard, I allocated an external Static IP address and registered a custom URL on a free dynamic DNS provider.

​

![](https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTNfMTQz/MDAxNzg5MzA0ODIwNDE4.3gfQZvAQTi15-LiPoN94hHCXYGO1L4gDkcFcAg7NEncg.uWFNIK44Cds9Gsk8lmpoRZCfWtkN7_QxPIaQ2rhtvesg.PNG/SE-6564e814-37b6-4b5e-a70e-7878e0e50c8e.png?type=w800)

​

This server was also configured to monitor system resource utilization externally via web interface.

​

![](https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTNfMjUw/MDAxNzg5MzA0OTQxOTkz.qrp0GCSAv_QInB7bwn8nWqKfnnW4NRxJ11ilwR1pKhkg.jomwV42U2WZRivxPf2hbi0Mn5BXEXgiKPcCZy6xIxkIg.PNG/SE-23e121ea-45a0-4f97-9165-355e2195f3e8.png?type=w800)

​

---

​

**Uniform Software Development Environment Accessible Anywhere, Anytime**

​

Previously, I wrote software by installing tools like GitHub Copilot or Google Antigravity locally on my desktop PC. However, the fatal limitation was having to be physically seated in front of that computer. Because algorithmic trading operates non-stop, I wanted the development environment itself to be accessible 24/7 from anywhere. To achieve this, I installed agy (Antigravity CLI) directly inside the Amazon cloud instance, allowing me to connect via SSH and code on the go.

​

![](https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTNfMjUw/MDAxNzg5MzA0NDEzMTY2.li8LOv68fliektyiCi2K7kt_vnlSzZVXzmd6iwGvoJUg.LBdUDA_5J6QytC5KE9QgGH6v163hmsYYnHdWtEm06agg.PNG/image.png?type=w800)

​

Once Antigravity CLI is installed on the Amazon Lightsail instance, it can be driven seamlessly in a terminal environment as shown below. You can log in via SSH from a PC, or open an SSH terminal app on a smartphone or tablet to manage development within an identical environment.

​

![](https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTNfMTEx/MDAxNzg5MzA0ODY0OTk3.CO1QOuoXOp_NX72Fxu1ynutUsYgrdiKrN8QC5qPsZPEg.m7zqABy9CWNCubT4nA04tGpMPdV-dBvisVk7AC6kF_Ug.PNG/image.png?type=w800)

​

---

​

**Service Monitoring and Emergency Control via Web Dashboard and Telegram**

​

I connected both a web dashboard and Telegram to the automated trading service to enable emergency stops and strategy modifications. While accessing the terminal via SSH on a phone or laptop is always an option, in urgent scenarios, being able to monitor state and trigger emergency overrides with simple chat messages is invaluable.

​

The web interface is structured to let me adjust various operational parameters and trading strategies required for automated order execution.

​

![](https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTNfMTE2/MDAxNzg5MzA0NjEzNzg4.wP2s9ukg2m3WA_dMg-5leBqGzXMK51vvUthic2tL-AMg.UsTECEfu7RvBTfNMtDCI5elaFRsT7Rro_WAycWreqDIg.PNG/image.png?type=w800)

​

Web Dashboard View

​

Telegram provides effortless, push-notification-based monitoring anytime, anywhere.

​

![](https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTVfMjYx/MDAxNzg5NDQzODY3ODMz.8khJ0hmMxtRAfVIhxTgPUfD7n4A6wD9m47-261LqRx0g.fxR5sMfqkH40s9RHEnkOhWa861WAlBrX14ak0Xb1020g.JPEG/SE-98221467-b0b7-11f1-ac60-536d5d4b9712.jpg?type=w800)
![](https://mblogthumb-phinf.pstatic.net/MjAyNjA5MTVfMzIg/MDAxNzg5NDQzOTgxOTk0.NnO99XUd8fwCZOqaQz2jUeEkmdp6SVQB0Kat-9RbYe8g.T95pk-Gjjg4DcFzhllHCp32qm45KRFndHbl_QntwAiUg.JPEG/SE-ecdc7311-b0b7-11f1-b6dc-6d83f3cb3215.jpg?type=w800)

​

---

​

To be clear, I am still an absolute beginner in investing with zero formal knowledge of stock market theory. While the current automated trading program looks neat and functional, formulating strategies that consistently generate real profit is something I am only beginning to learn—and it really is the hardest part. Nowadays, however, if you have the determination, modern AI makes assembling this entire setup surprisingly straightforward.

​

It has been running for about a week now. The initial foundational setup took only about two hours with AI assistance. Since then, I have been gradually resolving bugs, implementing trading strategies I am studying, and testing them one by one. It is truly astounding how easy it has become to build an algorithmic trading platform that would have seemed impossible for an individual just a few years ago.

​

My target return is 1% per month! I am testing short-term strategies without excessive greed, and if I achieve worthwhile results, I will be sure to share another update.

​

Thank you!
