---
title: "Study: US Option Trading Guide Part 1 - Nasdaq Futures and Options Synthetic Strategy"
date: 2026-01-02
category: "Economics Study"
categoryNo: 55
logNo: 224131971074
source: "https://m.blog.naver.com/sanjangboarder/224131971074"
thumbnail: "https://mblogthumb-phinf.pstatic.net/MjAyNTEyMDJfODcg/MDAxNzY3MzUwNDY1MDA0.NgYBxZSEO91bECg1-dKbb3sugXCreal13n392XvM0kog.yk6Avlzl_8SOSkxTO3gUD6_sjhOI754zwqP4Dl0SyjUg.PNG/image.png"
description: "Hello, this is SanjangBorder. Today, I share the first part of our US investment study series, outlining a synthetic hedging strategy combining Nasdaq futures and options."
lang: "en"
---

Hello, this is SanjangBorder.

​

Although I am an engineering graduate without professional financial training, I have decided to research economics concepts to prepare for future investments. I will be summarizing key financial topics, starting with those that interest me.

​

This initial post covers the NASDAQ futures and options markets.

​

---

​

### **Nasdaq Futures & Options Synthetic Strategy Guide (Theory & Practice)**

​

#### **Table of Contents**

​

1.  **Introduction**: Strategy Overview and Core Goals
2.  **Basic Structure**: Combining Futures and Options (Synthetic Position)
3.  **Core Theory 1**: Non-linear Payoff Structure (Linearity vs. Convexity)
4.  **Core Theory 2**: Option Greeks and the Law of Acceleration
5.  **Execution Strategy**: Elliott Wave and Dynamic Hedging
6.  **Practical Requirements**: Capital and Risk Management

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNTEyMDJfMTE5/MDAxNzY3MzUwNDI4NTM4.WqlxFuBK0bE4S17C77fIoIk7_jORVcoGITzXrBaEiwAg.2xbJRfmXBNbe-3E7pclDPjuapJJHKyh3mQU3KYUrjHog.PNG/image.png?type=w800" alt="Synthetic strategy guide diagram" />
</div>

​

---

​

#### **1. Introduction: Strategy Overview and Core Goals**

​

This guide outlines a **"Synthetic Hedge"** strategy designed to manage the volatility of NASDAQ futures using the leverage of options, aiming to capture returns during upward trends while protecting capital during market crashes.

​

Rather than simple diversification, this approach uses financial engineering concepts to adjust position allocations dynamically based on market conditions.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNTEyMDJfMzYg/MDAxNzY3MzUwNDM4NjAx.v71vLMXwFxXWWAMoTtepuxapvCE9xhWzTek0TaznvxUg.OhWQzN3zGh42Mmhi352hrFTOzrUdL9tLOeQShWFqRdwg.PNG/image.png?type=w800" alt="Market indicators analysis" />
</div>

​

---

​

#### **2. Basic Structure: Combining Futures and Options (Synthetic Position)**

​

##### **Theory: Protective Put**

​

The foundational configuration combines a **"Long Futures"** position with a **"Long Put"** option.

​

*   **Futures**: Generates returns as the index rises (acting as the engine).
*   **Options**: Restricts downside risk as the index falls (acting as the airbag).

​

> **Example**: An investor takes a long position on NASDAQ futures to profit from upward movements. Simultaneously, they pay a premium to buy put options. If the index crashes, the losses on the futures position are offset by the payout from the put options.

​

<div class="image-grid">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNTEyMDJfNTUg/MDAxNzY3MzUwNDU3NjQx.C4qvNIWsKROV__VymwRH1s3NPngC8cQQGAczaYvOpQog.l91ubOiWL_-ruRq_U4Lf-wev6k-oHfVRlegHVzAtEwYg.PNG/image.png?type=w800" alt="Protective put payoff curve" />
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNTEyMDJfODcg/MDAxNzY3MzUwNDY1MDA0.NgYBxZSEO91bECg1-dKbb3sugXCreal13n392XvM0kog.yk6Avlzl_8SOSkxTO3gUD6_sjhOI754zwqP4Dl0SyjUg.PNG/image.png?type=w800" alt="Synthetic long call comparison" />
</div>

​

---

​

#### **3. Core Theory 1: Non-linear Payoff Structure**

​

This strategy is effective because futures and options have different payoff profiles:

​

1.  **Futures (Linear)**: A 1% increase generates a 1% gain, and a 1% decrease results in a 1% loss (a linear relationship).
2.  **Options (Convexity)**: Downside losses are capped at the premium paid, while significant market drops generate exponential returns (a convex relationship).

​

**Key Concept**: During standard market conditions, the portfolio tracks the linear returns of the futures position. During market stress, the convex profile of the options position activates to shield the account.

​

---

​

#### **4. Core Theory 2: Option Greeks and the Law of Acceleration**

​

Managing a professional hedge requires tracking the Greeks derived from the Black-Scholes Model.

​

##### **1) Delta ($\Delta$, Speed)**

*   **Definition**: The change in option pricing relative to a 1-point move in the underlying index.
*   **Application**: Serves as the basis for calculating the number of option contracts required to offset the Delta risk of the futures position.

​

##### **2) Gamma ($\Gamma$, Acceleration) - *Most Critical***

*   **Definition**: The rate of change in Delta relative to moves in the underlying index.
*   **Application**: As the market declines, the sensitivity of the put options accelerates. This acceleration allows the options' gains to outpace the futures' losses during sharp drops, preserving capital.

​

> **Example**: If a market downturn is compared to a car descending a slope, the futures position represents a collision at 100 km/h (the loss), while the options position accelerates to 300 km/h in the opposite direction (the gain). This acceleration factor is calculated using the Black-Scholes formula.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNTEyMDJfMTAy/MDAxNzY3MzUwNDc2NjA4.x8UBs4IGDmcScXaWIW5g-Htr355yRyThz_SBTXZQQkQg.ttjBXc_vBTfRS1UeEdlpB51xduVhIYRm1YH4A3U8R6Mg.PNG/image.png?type=w800" alt="Greeks acceleration diagram" />
</div>

​

---

​

#### **5. Execution Strategy: Elliott Wave and Dynamic Hedging**

​

Rather than maintaining static ratios, allocations are adjusted dynamically based on market trends.

​

*   **Elliott Wave Theory**: Used to identify whether the market is in an impulsive or corrective wave.
*   **Dynamic Hedging**:
    *   **Bull Market (Impulse Waves)**: Reduce option allocations to lower premium costs.
    *   **Bear or Corrective Market**: Increase option allocations and acquire options with high Gamma values.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNTEyMDJfMjIx/MDAxNzY3MzUwNDg3NzA1.x9OsZNwThn1ER1CWN89kkq5m_qhjd7bJzFsLARaWNZ0g.hrjLcGkgtkx-L63KkdxIScwfynLnGSsprXBbPaLBxPsg.PNG/image.png?type=w800" alt="Dynamic hedging wave analysis" />
</div>

​

---

​

#### **6. Practical Requirements: Capital and Risk Management**

​

*   **Capital Requirements**: Trading E-mini NASDAQ (NQ) contracts requires significant capital (*typically hundreds of millions of KRW*). Retail traders can scale the strategy down using Micro E-mini contracts.
*   **Risks**: In a flat, low-volatility market, the portfolio will lose value daily due to time decay (Theta) on the long option positions.

​

<div class="single-image">
<img src="https://mblogthumb-phinf.pstatic.net/MjAyNTEyMDJf\u0036\u0039/MDAxNzY3MzUwNTAxODA3LjJNbTFUckxvVnRLVVVGUkdwTDh6NHNyWXJuWTFDelR3OHgtNHZuSHluMVFnLjRmMnFiaTFuMFNGYjJIMlI5SHJVdk9hVV9VbTFyczE3eVFvUzJnM0VnLlBORw==/image.png?type=w800" alt="Option time decay curve" /> (Wait! raw is `MjAyNTEyMDJfNjkg/...` -> yes)
</div>

​

While these strategies are complex for standard retail investors, the underlying concepts are useful. I plan to publish further posts exploring these financial theories.

​

Thank you.

​

#Nasdaq #OptionsHedging #SyntheticTrading #Greeks #DeltaHedging #Convexity #DynamicHedging #RiskManagement #TimeDecay #Theta
