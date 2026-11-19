# Clinic Appointment Assistant

A chatbot for patients of a clinic in Kigali: opening hours, services, prices, location, booking and cancelling a visit. Capstone of AITCD001 Chatbots Development, United African Institute of Technology.

## Live link

**https://clinic-assistant.streamlit.app** (opens without signing in; the first visitor may wait a minute while the app wakes up)

## Purpose and users

Patients of a clinic in Kigali ask the same questions all day: when it opens, how much a visit costs, where it is, how to book. The chatbot answers them at any hour, in English, Kinyarwanda or SMS spelling, so the receptionist can spend time on patients in front of her. It is a program, it says so at the top of the page, and it tells users that messages are recorded (Law N°058/2021). It gives no medical advice: in an emergency it sends the user to call or go to a hospital.

The clinic details (address, phone, prices, hours) are **invented for this project**.

## Intents

| Intent | What the user wants | Example messages |
|---|---|---|
| hours | When the clinic opens and closes | `what time do you open`, `mufungura saa ngapi`, `wat tym u open` |
| prices | What a service costs | `how much is dental`, `amenyo ni angahe`, `hw much 4 lab test` |
| services | What the clinic offers | `what services do you offer`, `mufite serivisi ki`, `do you have x ray` |
| location | Where the clinic is | `where are you`, `muri he`, `address?` |
| book | A visit (starts the booking conversation) | `i want to book a visit`, `ndashaka kwivuza`, `book visit 2moro` |
| cancel | Stop a visit or a booking | `cancel my appointment`, `hagarika`, `cancle` |
| emergency | Something urgent | `emergency`, `bleeding`, `ihutirwa` |
| out_of_scope | Everything else (goes to the fallback) | `who won the match`, `i want to complain` |

There are also two small intents handled by rules only: `greeting` (`muraho`) and `name` (`my name is Aline`).
Entities: SERVICE (consultation, dental, lab), DAY (monday to sunday, today, tomorrow), PLACE (kacyiru, kigali, nyabugogo).
The dataset (260 messages, 8 labels, 20 from real people) and the classifier training are in [`dataset/`](dataset/README.md).

## How it works

Every message goes through the same parts, in this order, and each reply says under it which part answered ("answered by"):

1. **Checks:** an empty or very long message gets a polite request; `bye` ends the conversation; `human` hands over to a person.
2. **The booking flow:** if a booking is in progress, the message is first read as the answer to the question asked.
3. **Rules:** patterns of words (`\bhow ?much\b`, `\bangahe\b`...), in priority order. One message with two requests is split ("what time do you open and how much is dental" gets both answers).
4. **Classifier:** if the rules find nothing, a TF-IDF (characters) + logistic regression model guesses the intent. It answers only if its confidence is at least **0.2**; the threshold is explained in `dataset/README.md`.
5. **Fallback:** if neither understands, the chatbot says so and what it can help with. The second time in a row it offers to connect a person.

If a handler fails with an error, the error is stored and the user gets a polite apology, never a crash.

**One dialogue flow: booking a visit**

```
book ──> Which service? ──> Which day? ──> Morning or afternoon? ──> Phone number?
                                                                         │
        "So: dental, monday, morning, 07xx. Shall I book it?" <──────────┘
              yes ──> request submitted, the receptionist will call
              no  ──> nothing is booked          cancel (at any step) ──> nothing is booked
```

A question can be asked in the middle (for example "where are you"): it is answered, and the booking question is asked again. Answers already in the first message are used ("book a dental visit" skips the service question).

| File | What it is |
|---|---|
| `streamlit/app.py` | the web page, the privacy notice, the log |
| `streamlit/chatbot.py` | the rules, the handlers (one function per intent), the flow, the classifier call |
| `streamlit/intent_classifier.joblib` | the trained classifier |
| `streamlit/requirements.txt` | the libraries Streamlit installs (scikit-learn pinned to the version that saved the classifier) |
| `dataset/` | `intents.csv`, the notebooks, the dataset README |
| `slides/` | the four slides (PDF) |

Every turn is sent to a private Google Sheet through a write-only Apps Script address. No key, token or Sheet address is in the repository: `LOG_URL` is set in Streamlit's Secrets. The raw log is never committed.

## Test results

Messages typed into the chatbot, with the part that answered each:

| Message | Intent | Answered by | Reply (start) |
|---|---|---|---|
| `what time do you open` | hours | rules | We are open Monday to Friday... |
| `mufungura saa ngapi` | hours | rules | We are open Monday to Friday... |
| `what time do you open and how much is dental` | hours + prices | rules | both answers in one reply |
| `do you treat teeth problems` | services | classifier (0.37) | We offer general consultation, dental care... |
| `ndashaka kubonana na dentist ejo` | book | classifier (0.40) | Which day? (the service was understood) |
| `do you have x ray` | services | classifier (0.42) | We offer general consultation... |
| `help my child is not breathing` | emergency | classifier (0.30) | This sounds urgent. Please call... |
| `who won the match` | out_of_scope | fallback | Sorry, I did not understand... |
| `asdfgh` | out_of_scope | fallback | Sorry, I still did not understand... (second time) |
| (empty message) | | validation | Please type a question. |
| `i can not come tomorrow anymore` | cancel (wanted) | classifier, **wrong**: book (0.21) | Which service? |
| `ndashaka kureka gahunda` | cancel (wanted) | rules, **wrong**: book | Which service? |

The last two are failures I found and kept as limits (see below).

### A bug found and fixed

**What happened:** the message `stop the appointment` started a booking: the chatbot answered "Which service?".
**The cause:** the `cancel` rule only knew "cancel", "hagarika" and "call it off". The word "appointment" matched the `book` rule instead. The same mistake was in the rule baseline of Portfolio Project 2 (`stop the appointment`, `remove my booking`).
**The change:** the words `stop`, `remove`, `undo` and `withdraw` were added to the `cancel` rule, which is above `book` in the table.

| | Before | After |
|---|---|---|
| `stop the appointment` | rules: book, "Which service?" | rules: cancel, "There is no booking in progress to cancel." |

A second change from testing: in the middle of a booking, `help my child is not breathing` was swallowed by the booking question. Now, when the rules find nothing during a booking, the classifier is asked, and an emergency or a cancel is answered at once.

## What users wrote and what changed

**TODO: fill in after the log is read and the classifier retrained** (notebook `dataset/Improve_from_log.ipynb`).

| | Before | After |
|---|---|---|
| Training rows | 212 | **TODO** |
| Test rows (unchanged) | 48 | 48 |
| Right / missed / wrong at threshold 0.2 | 31 / 11 / 6 | **TODO** |

Examples of what real users wrote (no names, no numbers) and the intent given:
- **TODO** `message` -> intent
- **TODO** `message` -> intent

The log has **TODO** turns from **TODO** visitors; **TODO**% reached the fallback.

## Limits and next improvement

- The classifier was trained on 212 messages and tested on 48, so its numbers move a lot with a few messages. It is only a little better than my rules (31 right against 29), and it gives more confident wrong answers (6 against 3).
- It confuses cancelling with booking when the message has no cancel word (`i can not come tomorrow anymore`), and misses short SMS messages (`wea r u`).
- `out_of_scope` is its weakest intent: its messages are all different, so there is no pattern to learn.
- The clinic facts are invented. The booking does not use a real calendar: it only sends a request that the receptionist would confirm.
- It gives no medical advice by design, and it cannot judge how serious an emergency is.
- Free hosting: the app sleeps when unvisited, and the first visitor waits.

**Next improvement:** collect more real messages for `cancel` and `out_of_scope` (from the log), label them, retrain, and keep the new model only if it scores better on the same test set. After that, connect booking to the clinic's real calendar.

**Running cost for real:** hosting an always-on app about 4 to 6 dollars a month, a domain about 10 to 20 dollars a year; the Google Sheet and the classifier are free. The real cost is the person who reads the log every week.


