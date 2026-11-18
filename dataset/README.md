# Intent dataset: Clinic Appointment Assistant

*Assignment 8, the first stage of Portfolio Project 2, Part 1.*

## The labels

| Label | What it means | Messages |
|---|---|---|
| hours | When the clinic opens and closes | 33 |
| prices | What a service or visit costs | 33 |
| services | What the clinic offers or treats | 34 |
| location | Where the clinic is and how to find it | 32 |
| book | Wanting a visit, a doctor or a slot | 33 |
| cancel | Stopping a visit or a booking | 31 |
| emergency | Something urgent about a person's body or safety | 32 |
| out_of_scope | Everything this chatbot does not answer | 32 |

## The labelling guideline

1. One message, one label. Two requests in one message: split it first.
2. Label the goal, not the words: 'is dental expensive' is prices, not services.
3. Asking what the clinic offers is services. Asking what it costs is prices, even if a service is named.
4. Wanting a visit, a doctor or a slot is book, even with a day or a service in it.
5. Stopping a visit or a booking is cancel. Changing it to another day is out_of_scope: the bot can only book or cancel.
6. Anything urgent about a person's body or safety (bleeding, breathing, accident) is emergency, even if it also asks for a visit.
7. Medical advice, test results, insurance or MoMo payment, complaints, jobs, lost property and chat: out_of_scope.
8. Keep the patient's words: typos, SMS, Kinyarwanda, as typed.

## Where the messages come from

| Source | Rows |
|---|---|
| rules | 9 |
| unmatched | 4 |
| local | 7 |
| people | 20 |
| written | 220 |

## Quality check

```
Per source: {'rules': 9, 'written': 220, 'local': 7, 'unmatched': 4, 'people': 20}
people: 20 of at least 20
Labels not in INTENTS: []
Duplicates: []
Conflicting labels: []
Balance, largest / smallest: 1.1
```

## Split and baseline

212 training, 48 test. My Portfolio Project 1 rules get **29 of 48** test
messages right. The messages they get wrong:

- `help my child is not breathing` (emergency): the emergency rule only knows "emergency", "bleeding", "can't breathe", "amaraso" and "ihutirwa", so other ways to say it are missed.
- `stop the appointment` (cancel): the rules say book, because the cancel rule only knows "cancel", "hagarika" and "call it off", and "appointment" matches book.
- `do you have a dentist` (services): the services rule needs "service", "offer", "serivisi", "mwivura" or "mufite", so this plain question is missed.

The rules only match the words I thought of, and many real messages use other words. A classifier can learn from the examples.

## Entities

SERVICE: consultation, dental, dentist, lab, laboratory, laboratwari, amenyo. Found in 39 messages of the dataset.
DAY: today, tomorrow, monday, tuesday, wednesday, thursday, friday, saturday, sunday. Found in 18 messages of the dataset.
PLACE: kacyiru, kigali, nyabugogo. Found in 6 messages of the dataset.

## What is still weak

- Messages from real people: only 20 of 260 rows (the rest I wrote), and cancel and emergency each have only 1 or 2 of them. Most people wrote full, correct sentences, so SMS-style messages are few.
- emergency has the least variety: many messages are short single words or similar sentences, and real emergencies may be typed very differently.
- PLACE appears in only 6 messages.
- Messages I was unsure how to label:
  - `i am sick and cant come`: cancel or out_of_scope (medical)? I chose cancel, because the goal is to stop the visit.
  - `i want to change my appointment to friday`: I chose out_of_scope, because the bot cannot reschedule.
  - `Ese mwakira abarwayi batabanje gufata gahunda?` (from a person): book or services? I chose book.
  - `Ese mufite serivisi z'imbangukiragutabara?` (from a person): services or emergency? I chose services.
  - `Can I get a refund if I cancel my appointment?` (from a person): cancel or out_of_scope? I chose out_of_scope.
  - `can i come on saturday morning`: book or hours? I chose book.
  - `do you accept mutuelle insurance`: prices or out_of_scope? I chose out_of_scope.


