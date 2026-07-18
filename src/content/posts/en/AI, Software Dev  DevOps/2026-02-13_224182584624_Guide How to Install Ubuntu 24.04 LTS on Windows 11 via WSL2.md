---
title: "Guide: How to Install Ubuntu 24.04 LTS on Windows 11 via WSL2"
date: 2026-02-13
category: "AI, Software Dev & DevOps"
categoryNo: 27
logNo: 224182584624
source: "https://m.blog.naver.com/sanjangboarder/224182584624"
thumbnail: "https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDVfMTEg/MDAxNzcwMjk5MjAwMjM1.wGXrFNaV8o5rrH118ULOUBWg8EabHIRjR_69dVJ_KHog.fCQUBH-byATK4QHF6dfwrp6ho-1Sapkj1Vg9Nrdr8ocg.PNG/image.png"
description: "Hello, this is SanjangBorder. Today, I share a guide on how to install Ubuntu 24.04 LTS on Windows 11 using WSL2. I cover basic setup, resource allocation configs, and resolving virtual drive storage issues."
lang: "en"
---

Hello, this is SanjangBorder.

​

In this post, I share my experience installing a Linux environment on Windows using a Virtual Machine (VM). Since I follow AI trends closely, I wanted to test **OpenClaw**, an autonomous AI agent framework that is granted control over local PC or server resources.

​

OpenClaw and Meltbot have received substantial attention since early February. In simple terms, you can think of it as an early-stage open-source version of JARVIS. Since the agent currently runs best on macOS or Linux, I briefly considered purchasing an Apple Mac Mini M4. However, I decided instead to build a Linux VM on my Windows PC.

​

Since most users operate on Windows, running Linux requires a VM or a container setup. While I was familiar with using VMware, I discovered that Windows supports WSL2 (Windows Subsystem for Linux 2), which allows you to run Linux environments with minimal overhead. I proceeded with this method.

​

The installation process is straightforward. Open the Windows PowerShell console as administrator and execute `wsl --install`, followed by a system reboot.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDVfMjkx/MDAxNzcwMjk4MjAxNzQ0.m-apvYGMaLDQ9O-jOzB_GoLSIXOiCgQubiEcbqC4oJ0g.97ydy_ktQeDIkXKaHnj2k3qRjNc04hYi9xVPKsQsAE0g.PNG/image.png?type=w800" alt="PowerShell wsl install command" />
</div>

​

Once WSL is installed, search for "Ubuntu" in the Microsoft Store. I selected **Ubuntu 24.04 LTS**, which is the stable release. The store handles the download and initial setup, which was a smooth experience compared to manual installations in the past.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDVfMTI0/MDAxNzcwMjk4ODYyMDI0.alFKUMkbf3SH3kMbgyguM4Qf2pjoeioFzZq8fypsMg4g.Yjn4GdSyuFVi6OLv_xvX9rADZRnafLSj84_cab70pxAg.PNG/image.png?type=w800" alt="Microsoft Store Ubuntu download page" />
</div>

​

After installing Ubuntu from the store, you configure the WSL environment settings. You can allocate RAM, CPU cores, and storage limits. If you are unsure about the parameters, using the default settings is recommended.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDVfMjMw/MDAxNzcwMjk4ODY5NTY0.dGLXbpAb-zmjdN72uVmTUMWpthyoGxzgysKxr9TxYUkg.U9koe0lGFMQP_0hOB0ewUi9W67kdM3EFIejzBCoiWmwg.PNG/image.png?type=w800" alt="Ubuntu initialization in terminal" />
</div>

​

Detailed documentation from Microsoft can be found at the link below.

​

🔗 [Official Documentation: Windows Subsystem for Linux Documentation](https://learn.microsoft.com/ko-kr/windows/wsl/)

​

You can adjust the core count allocation. I use an Intel i5-12600K CPU, which features 10 physical cores and 16 threads, allowing up to 16 virtual processors in WSL. Since this Ubuntu environment is not running enterprise services, allocating 4 cores is sufficient for general development tasks. You can scale it up if your workload requires it.

​

For memory allocation, a ratio of 2GB RAM per allocated core is a solid starting point, meaning an 8GB allocation is appropriate for a 4-core setup. For storage, you configure the virtual disk size, which should be set lower than the available physical storage space on the host drive.

​

By default, the virtual disk allocates approximately 1TB of virtual space, even if the physical host drive only has 200GB of free space. Because this is a dynamically expanding virtual disk, the guest OS will encounter write errors once the physical host drive is depleted. It is best to align these values.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDVfODkg/MDAxNzcwMjk5MTI3Nzcz.vAj6rwEX2cit3X8RKwNhAjektS5Wgr4xubGFmljZ5acg.oHM1RW6tQIKq5oDG71XIuZpVdibBj6J1FF-e8jC6n00g.PNG/image.png?type=w800" alt="WSL status output details" />
</div>

​

While WSL2 simplifies running Ubuntu, it does not include a graphical desktop interface by default. It opens a command-line console. As a former software developer, I am familiar with the terminal, but other users may find it inconvenient. Note that running GUI applications is supported via X11 forwarding or WSLg depending on your requirements.

​

First, I verified the virtual CPU core configuration.

​

<div class="image-grid">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDVfNjYg/MDAxNzcwMjk5MTA0MjYy.14j5dSbDGc2G6glgG_xIvNQHbDGatzOeGwfz8-4Sc0og.myztfkCGPgCAeycM7Fq_-1604a5IsTlNFepK_aTnH8gg.PNG/image.png?type=w800" alt="Checking CPU core count command" />
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDVfMzIg/MDAxNzcwMjk5MDk0NDg0.X27RNLaqM4hmt9mMGEpTtHbXPmP6bsDbeylVb9f91Nsg.1VCFKTXktcdkarpnuu_1jg1MsVMS8musLIzi9WiDXJEg.PNG/image.png?type=w800" alt="Verifying system specifications" />
</div>

​

I also checked the OS version details. The installation process is straightforward. Compared to older methods that required disk partitioning and dual-boot configurations, the virtualized setup is much simpler.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDVfMTEg/MDAxNzcwMjk5MjAwMjM1.wGXrFNaV8o5rrH118ULOUBWg8EabHIRjR_69dVJ_KHog.fCQUBH-byATK4QHF6dfwrp6ho-1Sapkj1Vg9Nrdr8ocg.PNG/image.png?type=w800" alt="Checking OS version information" />
</div>

​

Using the default configuration, `/dev/sdd` was allocated 1TB, as shown below. The physical drive only had 400GB of free space. Since I wanted to avoid potential errors, I adjusted the storage configuration.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDVfMTE5/MDAxNzcwMjk5Mjc2NTIy.kS-HFK3CtBT7kkwze9jxBgnFNWNOVtKyrI5jBFx0hBsg.Btwl4fY8hqtZbs2X_feLxFAmW_NbJH85QPjm3-LvOVcg.PNG/image.png?type=w800" alt="DF command disk output" />
</div>

​

Consulting Gemini, I obtained steps to adjust the WSL configuration. I shut down the WSL instance and attempted to move the virtual disk file (*ext4.vhdx*) to my D drive, which had more physical storage space.

​

<div class="image-grid">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDdfODUg/MDAxNzcwNDI3MTkzNTky.bFwJSqqjlOhMvDPUeN5MEjJ5ro2KL7e-2K0NQEJ8DTIg.5Lb26ifHVw5MI3cXF8iSoIh-MPDNJiLdwSU9UeSOuiIg.PNG/image.png?type=w800" alt="Exporting virtual disk files" />
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDdfMzA3/MDAxNzcwNDI3MjM1MTY4.0VcoT35yVLUO9V6cPHriwsZjM9rNzehVsMrVeVo3NfEg.BpwGOebHv0H6U00c2_ujc6QqzSIad80moG_nyp3L00cg.PNG/image.png?type=w800" alt="Importing to D drive" /> (Wait! raw is `MDAxNzcwNDI3MjM1MTY4` -> yes, copy exact `MjAyNjAyMDdfMjA3` -> wait, the tool output was `MjAyNjAyMDdfMjA3` -> yes, copy exact `MjAyNjAyMDdfMjA3`)
</div>

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDdfMTk2/MDAxNzcwNDI3MjQwNDc5.i7EJb_ZPKL-izxEzHEe71tlK_VaaVJ_Esq7xt5iEWQwg.R8xnMlpwCSJSdAnIMvaAv3kffOe_PPvcsm461effbnAg.PNG/image.png?type=w800" alt="Confirming file transfer completion" />
</div>

​

However, I encountered a startup error, suggesting a configuration mismatch in the hypervisor environment.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDdfMTk5/MDAxNzcwNDI3NjMwODAz.4XS_2RsTb_GCCvwUSYS1E3VVBgTV_D_1-iVEP9BJS_gg.SKF3x0VKfvAryprIz-ArXTQFNtVxKnxBEy79g6xO2WIg.PNG/image.png?type=w800" alt="Terminal boot error screen" />
</div>

​

I consulted Gemini again, identified the necessary changes in the Windows Registry, and updated the paths.

​

<div class="image-grid">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDdfMjU0/MDAxNzcwNDI3NTkyNDU0.kU5BlSkNHPMwEqWD4E812yl4iU-bwWZLVo1A00DSDjsg.jxb9iuTOUF4BF5qvZq_F_b50Frvj58J8IZ-6zM8pvWsg.PNG/image.png?type=w800" alt="Editing Registry Editor path" />
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDdfMjAx/MDAxNzcwNDI3NTY1NjIx.aBXB4BfYxgmG69hVthD8ttIoOpYNt8GUsQFPe-rNqHsg.a6Ob2N1d7Iu254DpSpHOqPFJGSAM-Kp65ufKUH-cefAg.PNG/image.png?type=w800" alt="Registry path corrected view" />
</div>

​

After applying the registry fixes, the instance initialized successfully.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDdfNzMg/MDAxNzcwNDI3NzU4NDQ0.4autNrZL95lf41TU5xVT0mmikSzWDEweZ9E7-UuGlh4g.aodKIXDwt6hiMBbCNSe3LoLUyLviDqRpFwT-m900n4kg.PNG/image.png?type=w800" alt="Successful terminal login prompt" /> (Wait! raw is `MDAxNzcwNDI3NzU4NDQ0` -> yes, copy exact)
</div>

​

However, since the D drive also lacked a full 1TB of physical space, I attempted to shrink the virtual disk partition.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDdfMzUg/MDAxNzcwNDI3NzQyNTk1.iuORIzWjAzwKoZ2NPHveW-DMt7mWGst3Epsc31VJIi0g.9ix1KDprQJPbTbnrwmLOUVqwKf_P2hVkao0s6g9RYcQg.PNG/image.png?type=w800" alt="Verifying disk sizes" />
</div>

​

I tested several partitioning commands, but they failed due to dependency mismatches. The configuration steps became too complex.

​

<div class="image-grid">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDdfMjcy/MDAxNzcwNDI4MzA1MjA2.eVqogcImHa9m8_gYK7L9cszeO3TI0y-MDLawS-P1qKYg.R2yNxAN7pHH13PRtt8xxSCKh87sxCBUG09Tm1YiGKFYg.PNG/image.png?type=w800" alt="Command failure logs" />
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNjAyMDdfMjAy/MDAxNzcwNDI3ODE0Nzc4.kdkTkL5XmIenTabG3tHq98T-Jwt_R7enxxmGwqzGpwUg.tITDdBrOEWZR1DcMrZqMwZt48n9Il86bjVs62BV1npwg.PNG/image.png?type=w800" alt="Shrinking disk failure logs" />
</div>

​

Ultimately, I chose to unregister the instance and reinstall Ubuntu from scratch, which resolved the storage size allocation issue cleanly. I obtained the desired setup.

​

WSL2 on Windows 11 provides a convenient platform for running virtualized Ubuntu environments. If you want to experiment with open-source tools that require a Linux environment, WSL2 is a solid option to consider.

​

Thank you.
