# Clinic Appointment Assistant

> A rule-based chatbot that helps patients of a clinic in Kigali find opening hours, services, prices and the address, and request an appointment, and that hands over to a member of staff when it cannot help.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/USERNAME/REPOSITORY/blob/main/clinic_chatbot.ipynb)

![A conversation with the chatbot](demo.png)

---

## The problem it solves

Patients of a small clinic usually have to phone or queue at the reception just to ask the opening hours, the price of a service or where the clinic is. This chatbot answers those fixed questions at any time, in English or Kinyarwanda, and collects the details of an appointment request, so the receptionist only handles real conversations. It never gives medical advice, and it sends emergencies straight to a phone number and the nearest hospital.

*The clinic, its address, phone number, hours and prices in this project are invented for the course.*

## What it can do

| Intent | A customer might type | The chatbot replies |
|---|---|---|
| greeting | `muraho`, `hello`, `mwiriwe` | Says it is a computer program and what it can help with |
| name | `my name is aline` | `Nice to meet you, Aline.` and uses the name later |
| hours | `what time do you open`, `mufungura saa ngapi`, `wat tym u open` | Monday to Friday 08:00 to 17:00, Saturday 08:00 to 13:00, closed Sunday |
| prices | `how much is dental`, `amenyo ni angahe`, `hw much 4 dental` | The price of the service named (dental 10,000 RWF), or all prices if none is named |
| services | `what services do you offer`, `mufite serivisi` | General consultation, dental care and lab tests |
| location | `where are you`, `clinic location please`, `muri he` | The address and the phone number |
| book | `i want an appointment`, `ndashaka kwivuza`, `book a dental visit` | Starts the booking conversation (see below) |
| cancel | `cancel`, `hagarika` | Cancels the booking in progress; nothing is booked |
| emergency | `emergency`, `bleeding`, `ihutirwa` | Tells the user to call the clinic or go to the nearest hospital now |

## How it works

- **Recognising requests:** a table of patterns (`RULES`), tried in order, and the first match wins. `emergency` is at the top so that a danger word is never taken for something else, and `cancel` is above `book` so that "cancel my appointment" cancels instead of starting a booking. Specific intents (`prices`) are above general ones (`services`). Every pattern uses `\b` around words, and the text is first cleaned (lowercase, no punctuation) so that capitals and punctuation do not matter. One message can hold two requests ("what time do you open and how much is dental"), and each is answered.
- **Answering:** a router of handler functions (`HANDLERS`), one per intent. `handle_prices` reads the message: it looks for the service named (using a dictionary of words such as `dental`, `amenyo`, `dentist`) and works out the price, so the answer depends on what the user typed.
- **Conversation:** booking is a short conversation of four questions: service, day, time and phone number. Each answer must match a pattern, otherwise the question is asked again (for example, Sunday is refused because the clinic is closed). At the end the bot shows a summary and asks for **yes or no**; nothing is submitted until the user says yes. The user can type `cancel` at any point, `bye` to leave, or `human` to ask for a member of staff. A side question during the booking (such as "where are you") is answered, and then the bot asks the pending question again.
- **Memory:** during a conversation it remembers the user's name, the last intent (so that "and lab?" after a price works) and how many times in a row it failed to understand. It also keeps the booking answers until the booking ends. All of it is forgotten when the conversation ends. The bot only asks for a phone number, and only inside the booking.
- **When things go wrong:** empty, symbol-only and very long messages get a polite reply. The first time the bot does not understand it says what it can help with, the second time it offers a member of staff, and every message it did not understand is saved in the `UNMATCHED` log. Each handler runs inside `try` and `except`, so an error is saved in `ERROR_LOG` and the user sees an apology instead of a crash.

## Try it

1. Click **Open in Colab** at the top of this page.
2. Run the cells in order, from the top (Runtime, then Restart and run all).
3. Run the chat cell (Step 11) on its own and type a question.

## Testing

Ten test conversations, written before they were run (the expected result of each is written in a comment at the top of Step 8 of the notebook).

- Passed: **9** of 10 on the first run
- The ones that failed, and why:

| Conversation | What happened | Why |
|---|---|---|
| Test 10: `book a dental visit` | The bot asked "Which service?" even though the user had already said dental | The booking handler only started the conversation. It did not read the message for answers already given |

The ten conversations are: a greeting, a name and a goodbye; two requests in one message; a booking confirmed; a booking refused at the end; a side question during the booking; cancelling halfway; a follow-up question ("and lab?"); empty and unknown input and then `human`; Kinyarwanda phrasing and an emergency; and a booking with the service already given.

## A bug found and fixed

**What happened:** in test 10, the user typed `book a dental visit` and the bot still asked "Which service? Consultation, dental or lab test?".

**The cause:** `handle_book` called `start_flow()` and returned the first question. It never looked at the request, so the service already in the message was ignored.

**The change:** `handle_book` now starts the flow and then keeps answering each question from the same request for as long as the request contains a valid answer. After the change, test 10 was run again and the bot went straight to "Which day?".

## Known limitations

- Spelling mistakes in the service name, such as `deental`, are not understood. The bot then lists all the prices instead of the dental price.
- A follow-up such as `and lab?` is ignored while a booking is in progress. It works only outside the booking.
- Messages such as `nshaka umuganga` and `pls help me` end up in the `UNMATCHED` log, because no rule has their words.
- The replies are in English only, even when the user writes in Kinyarwanda.
- The bot does not check that Saturday afternoon is outside the opening hours (the clinic closes at 13:00 on Saturday).
- The appointment request is only confirmed in the conversation. It is not saved or sent to a real receptionist, because this is a course project.

## What comes next

- Reply in Kinyarwanda when the user writes in Kinyarwanda, and tolerate spelling mistakes.
- Run the chatbot on Telegram or WhatsApp, and save the appointment requests to a file or a spreadsheet for the receptionist.

## Built with

Python 3 · the `re` module · Google Colab

## About

Built by Ishimwe Mwambutsa Daniella for the Chatbots Development module (AITCD001), AI Technology Certification, United African Institute of Technology, Kigali. October 2026.

