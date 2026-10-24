# Presentation Script — Decision Dashboard for Urban Food Production
### Ruthvik Savaram | Y247K345

**How to use this:** Each slide has one **memory hook** (one word) — if you blank out, just remember the hook and the rest will come back to you. Say it like you're talking to a friend, not reading a script.

---

## 1. Title — Hook: **"Intro"**

"Hi, I'm Ruthvik. My project is a decision dashboard that helps figure out the best spots for urban food production across the Kansas City metro area."

---

## 2. Introduction & Problem Statement — Hook: **"Gap"**

"So here's the problem — food access isn't the same everywhere in KC. It depends on income, transit, how close you live to a grocery store.

To fix that, you'd want to compare where the land is available with where people actually need it most. But that data lives in different places, at different scales — it doesn't line up on its own.

So this project uses something called Multi-Criteria Decision Making to pull it all together into one clear score per location."

---

## 3. Project Objectives — Hook: **"5 Steps"**

"There are five steps to this. Organize the data, explore it, run spatial analysis at two levels, combine it all into a suitability score, and put it in an interactive dashboard."

---

## 4. Data Sources & Tools — Hook: **"Where from"**

"The data covers five things — demographics, socioeconomics, health, food access, and built environment.

I'll look at the big picture using Census Tracts, and get specific about individual pieces of land using parcel data — ORKA for the Kansas side, KCMO's Parcel Viewer for Missouri.

For tools, I'm using ArcGIS Online to do the analysis and build the dashboard, and Python or R to help prep the data.

And — just to be upfront — I don't have the actual dataset yet. Getting it is my next step. What I'm showing today is the plan."

---

## 5. Methodology — Hook: **"The Engine"**

"This is really the core of the project — four steps.

First, I clean up the data so everything's on the same scale and comparable.

Second, I use something called AHP to decide how much each factor should matter — like, should food access count for more than empty land?

Third, those weights get combined into one suitability score for each location.

Fourth, all of that goes into a dashboard where you can actually move the weights around and watch the map update live."

---

## 6. Expected Outcomes — Hook: **"What you get"**

"End result — the dashboard gives you four things: a suitability score, the ability to compare areas side by side, a way to dig into what's driving a score, and live reweighting.

So basically, a planner could ask 'what if food access mattered more?' and see the answer right away."

---

## 7. Learning Goals & Project Status — Hook: **"Honesty"**

"For me personally, this builds my skills in data analysis, spatial analysis, MCDM, and dashboard building.

On where things stand — the plan is done, that's what I just walked you through. Next step is actually getting the data, since I haven't run this on real numbers yet. After that: explore it, score it, build the dashboard."

---

## 8. Thank You — Hook: **"Close"**

"That's my proposal. Happy to take any questions."

*(Pause. Don't rush to fill the silence.)*

---
---

# Quick Q&A Cheat Sheet

**Why MCDM/AHP, not something simpler or ML?**
"AHP handles competing factors in a structured way. ML would need past outcome data I don't have."

**How do you know the scores are accurate?**
"I'll test how much results change if I shift the weights, and check high scores against known food deserts."

**What if the dataset doesn't arrive in time?**
"I'd fall back on public data — Census and the open ORKA/KCMO parcel data — to still show the full process."

**Do you have the data yet?**
"Not yet — that's my immediate next step."

**How do tract-level and parcel-level data work together?**
"Tracts give the big picture, parcels give site-specific detail. I connect a parcel to its tract when I need both."

**How do you compare things measured differently?**
"I normalize everything to the same 0–1 scale before combining it."

**Who sets the weights?**
"I'll set starting weights based on research, but users can adjust them in the dashboard."

**What if two factors conflict?**
"The score balances everything — nothing scores high just because of one strong factor."

**How many variables will you use?**
"Probably 8 to 12, once I see what actually stands out in the data."

**Who's this for?**
"Mainly city planners and researchers, but it's usable by community groups too."

**Will it be public?**
"That's up to the research team — ArcGIS Online supports either."

**Biggest risk right now?**
"Getting the dataset on time — everything else depends on it."

**What have you learned even without the data yet?**
"Mostly the method — how AHP and MCDM connect, and what ArcGIS Online can actually do."
