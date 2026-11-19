"""Clinic Appointment Assistant: the chatbot logic (no Streamlit here, so it can be tested).

Order of one turn: validate -> exit -> person -> flow -> RULES -> follow up -> CLASSIFIER -> FALLBACK.
Every reply says who produced it ("answered by").
"""
import re

# ---------------------------------------------------------------- PART 1: the domain
BOT_NAME = "Clinic Appointment Assistant"
USERS = "patients of a clinic in Kigali"
TOPICS = "opening hours, services, prices, location and booking a visit"

# NOTE: these clinic details are invented. Replace them with the real ones.
PHONE = "07XXXXXXXX"
ADDRESS = "KG 567 St, Kacyiru, Kigali"
PRICES = {"consultation": "5,000 RWF", "dental": "10,000 RWF", "lab": "7,000 RWF"}
ALIASES = {"consultation": "consultation", "general": "consultation",
           "dental": "dental", "dentist": "dental", "amenyo": "dental",
           "lab": "lab", "laboratory": "lab", "laboratwari": "lab"}
SERVICE_WORDS = r"\b(" + "|".join(ALIASES) + r")\b"

# ---------------------------------------------------------------- PART 2: the classifier
THRESHOLD = 0.2          # chosen in Portfolio Project 2 Part 1 (see dataset/README.md)

# ---------------------------------------------------------------- PART 3: the rules
RULES = [
    ("name",      r"\bmy name is\b"),
    ("emergency", r"\bemergency\b|\bbleeding\b|\bcan ?t breathe\b|\bamaraso\b|\bihutirwa\b"),
    ("cancel",    r"\bcanc\w*\b|\bhagarika\w*\b|\bcall it off\b|\bstop\b|\bremove\b|\bundo\b|\bwithdraw\b"),
    ("hours",     r"\bhours?\b|\bopen\w*\b|\bclos\w*\b|\bwhat ?time\b|\bwat ?tym\b|\bsaa ngapi\b|\bamasaha\b|\bgufungura\b"),
    ("prices",    r"\bprices?\b|\bcosts?\b|\bfees?\b|\bhow ?much\b|\bhw ?much\b|\bangahe\b|\bibiciro\b"),
    ("services",  r"\bservices?\b|\bserivisi\b|\boffer\w*\b|\bmwivura\b|\bmufite\b"),
    ("location",  r"\bwhere\b|\blocat\w*\b|\baddress\b|\bmuri he\b|\bmuherereye\b"),
    ("book",      r"\bbook\w*\b|\bappointments?\b|\bvisit\b|\breserv\w*\b|\bgahunda\b|\bkwiyandikisha\b|\bkwivuza\b"),
    ("greeting",  r"\bhello\b|\bhi\b|\bhey\b|\bmuraho\b|\bmwaramutse\b|\bmwiriwe\b"),
]
FOLLOW_UPS = {"prices": SERVICE_WORDS}       # "and lab?" after a price

# ---------------------------------------------------------------- PART 4: the booking flow
FLOW_STEPS = [
    ("service", "Which service? Consultation, dental or lab test?", SERVICE_WORDS),
    ("day", "Which day? Monday to Saturday. We are closed on Sunday.",
     r"\b(monday|tuesday|wednesday|thursday|friday|saturday|today|tomorrow)\b"),
    ("time", "Morning or afternoon?", r"\b(morning|afternoon)\b"),
    ("phone", "What is your phone number? For example 07XXXXXXXX.", r"\b07\d{2} ?\d{3} ?\d{3}\b"),
]
DONE = "Your appointment request is submitted. The receptionist will call you to confirm: "
NOT_DONE = "No problem. Nothing has been booked."
YES = r"\b(yes|yeah|yego|correct|ok|okay)\b"
NO = r"\b(no|nope|oya|wrong)\b"

# ---------------------------------------------------------------- PART 5: text helpers
MAX_LENGTH = 300
ASK_AGAIN = f"Please type a question. I can help with {TOPICS}."
IN_WORDS = "Please type your question in words."
TOO_LONG = "That is a long message. Could you ask one thing at a time?"
SORRY = "Sorry, something went wrong on my side. Please try again, or type 'human'."
FALLBACK = f"Sorry, I did not understand. I can help with {TOPICS}."
STILL_LOST = (f"Sorry, I still did not understand. Type 'human' for a member of staff, "
              f"or ask about {TOPICS}.")
HANDOVER = "Connecting you to a member of staff. They can see this conversation."
EXIT_WORDS = ("bye", "goodbye", "exit", "quit", "thanks", "murakoze")
HUMAN_WORDS = ("human", "staff", "agent", "person")
CONNECTORS = r"\band\b|\bbut\b|\balso\b|\bthen\b|[?]"


def normalise(text):
    """Remove punctuation (keeping the colon of 21:00), lowercase, trim."""
    return re.sub(r"[^\w\s:]", "", text).lower().strip()


def new_state():
    """One conversation's memory. Each visitor gets their own."""
    return {"flow": {"step": None, "collected": {}},
            "context": {"name": None, "last_intent": None, "fallbacks": 0}}


# ---------------------------------------------------------------- the flow machinery
def start_flow(state):
    state["flow"]["step"] = 0
    state["flow"]["collected"] = {}
    return FLOW_STEPS[0][1]


def reset_flow(state):
    state["flow"]["step"] = None
    state["flow"]["collected"] = {}


def summary(state):
    return ", ".join(state["flow"]["collected"].values())


def continue_flow(message, state):
    """One answer: store it, ask the next question, and at the end, confirm."""
    flow = state["flow"]
    text = normalise(message)
    if flow["step"] == "confirm":
        if re.search(YES, text):
            booked = summary(state)
            reset_flow(state)
            return DONE + booked + ". Thank you."
        if re.search(NO, text):
            reset_flow(state)
            return NOT_DONE
        return "Please answer yes or no."
    name, question, pattern = FLOW_STEPS[flow["step"]]
    found = re.search(pattern, text)
    if not found:
        return question                      # not a valid answer: ask again
    flow["collected"][name] = found.group()
    flow["step"] = flow["step"] + 1
    if flow["step"] < len(FLOW_STEPS):
        return FLOW_STEPS[flow["step"]][1]   # the next question
    flow["step"] = "confirm"
    return "So: " + summary(state) + ". Shall I book it? Yes or no."


# ---------------------------------------------------------------- the handlers: one per intent
def handle_emergency(text, state):
    reset_flow(state)
    return f"This sounds urgent. Please call {PHONE} or go to the nearest hospital now."


def handle_hours(text, state):
    return ("We are open Monday to Friday 08:00 to 17:00, and Saturday 08:00 to 13:00. "
            "We are closed on Sunday.")


def handle_prices(text, state):
    """Reads the message: the price of the service named, if it is one we offer."""
    found = re.search(SERVICE_WORDS, text)
    if found:
        service = ALIASES[found.group(1)]
        return f"{service.capitalize()} costs {PRICES[service]}."
    return "Consultation 5,000 RWF, dental 10,000 RWF, lab test 7,000 RWF."


def handle_services(text, state):
    return "We offer general consultation, dental care and lab tests."


def handle_location(text, state):
    return f"We are at {ADDRESS}. You can call us on {PHONE}."


def handle_book(text, state):
    """Starts the booking conversation; answers already in the request are used."""
    if state["flow"]["step"] is not None:
        return "Your booking is already under way."
    reply = start_flow(state)
    while state["flow"]["step"] != "confirm":
        pattern = FLOW_STEPS[state["flow"]["step"]][2]
        if not re.search(pattern, text):
            break
        reply = continue_flow(text, state)
    return reply


def handle_cancel(text, state):
    if state["flow"]["step"] is not None:
        reset_flow(state)
        return "Your booking has been cancelled. Nothing was booked."
    return "There is no booking in progress to cancel."


def handle_name(text, state):
    found = re.search(r"\bmy name is (\w+)", text)
    if found:
        state["context"]["name"] = found.group(1).capitalize()
        return f"Nice to meet you, {state['context']['name']}."
    return "Sorry, I did not catch your name."


def handle_greeting(text, state):
    if state["context"]["name"] is not None:
        return f"Muraho, {state['context']['name']}! How can I help?"
    return (f"Muraho! I am the {BOT_NAME}, a computer program. "
            f"I can help with {TOPICS}.")


HANDLERS = {
    "emergency": handle_emergency, "cancel": handle_cancel, "hours": handle_hours,
    "prices": handle_prices, "services": handle_services, "location": handle_location,
    "book": handle_book, "name": handle_name, "greeting": handle_greeting,
}
ASKS = ["book"]      # intents whose reply is a question: it goes last


# ---------------------------------------------------------------- the rules: matching and routing
def match(message):
    """The tag of the first rule that matches, or "fallback"."""
    text = normalise(message)
    for tag, pattern in RULES:
        if re.search(pattern, text):
            return tag
    return "fallback"


def route(message):
    """One (intent, request) pair for each request understood (several in one message)."""
    found = []
    seen = []
    for part in re.split(CONNECTORS, message.lower()):
        part = normalise(part)
        if part == "":
            continue
        tag = match(part)
        if tag != "fallback" and tag not in seen:
            seen.append(tag)
            found.append((tag, part))
    return found


def safe_handle(tag, request, state, errors):
    """Run one handler. If it fails, log the error and apologise instead of crashing."""
    try:
        return HANDLERS[tag](request, state)
    except Exception as error:
        errors.append(repr(error))
        return SORRY


def respond(found, state, errors):
    """Answer every request found; a reply that asks a question goes last."""
    answers, questions = [], []
    for tag, request in found:
        reply = safe_handle(tag, request, state, errors)
        (questions if tag in ASKS else answers).append(reply)
    return " ".join(answers + questions)


def follow_up(text, state):
    last = state["context"]["last_intent"]
    if last in FOLLOW_UPS and re.search(FOLLOW_UPS[last], text):
        return [(last, text)]
    return []


def fallback(state):
    state["context"]["fallbacks"] += 1
    return STILL_LOST if state["context"]["fallbacks"] >= 2 else FALLBACK


def validate(message):
    """A reply if the message cannot be used; None if it can."""
    if message is None or message.strip() == "":
        return ASK_AGAIN
    if normalise(message) == "":
        return IN_WORDS
    if len(message.strip()) > MAX_LENGTH:
        return TOO_LONG
    return None


# ---------------------------------------------------------------- the classifier
def classify(classifier, message):
    """(intent, confidence) from the trained model, or (None, 0.0) without one."""
    if classifier is None:
        return None, 0.0
    row = classifier.predict_proba([normalise(message)])[0]
    best = row.argmax()
    return str(classifier.classes_[best]), float(row[best])


# ---------------------------------------------------------------- one complete turn
def reply_to(message, state, classifier=None, errors=None):
    """Return (reply, answered_by, intent, confidence)."""
    errors = errors if errors is not None else []
    problem = validate(message)
    if problem is not None:
        return problem, "validation", "", 0.0
    text = normalise(message)
    ctx = state["context"]

    if text in EXIT_WORDS:                                   # 1. the end, at any point
        name = ctx["name"]
        reset_flow(state)
        state["context"] = {"name": None, "last_intent": None, "fallbacks": 0}
        thanks = f"Thank you, {name}. Murakoze." if name else "Thank you for contacting us. Murakoze."
        return thanks, "exit", "exit", 1.0

    if text in HUMAN_WORDS:                                  # 2. a person, at any point
        reset_flow(state)
        return HANDOVER, "human", "human", 1.0

    if state["flow"]["step"] is not None:                    # 3. the booking flow sees it first
        step_before = state["flow"]["step"]
        flow_reply = continue_flow(message, state)
        if state["flow"]["step"] != step_before:
            return flow_reply, "flow", "book", 1.0
        found = route(message)
        if len(found) == 0:
            # the rules found nothing: an urgent or cancel message must not be lost in the flow
            intent, confidence = classify(classifier, message)
            if intent in ("emergency", "cancel") and confidence >= THRESHOLD:
                return safe_handle(intent, text, state, errors), "classifier", intent, confidence
            return flow_reply, "flow", "book", 1.0
        reply = respond(found, state, errors)
        if state["flow"]["step"] is not None:
            reply = reply + " " + flow_reply
        return reply, "rules", found[-1][0], 1.0

    found = route(message)                                   # 4. the rules
    if found:
        ctx["fallbacks"] = 0
        ctx["last_intent"] = found[-1][0]
        return respond(found, state, errors), "rules", found[-1][0], 1.0

    found = follow_up(text, state)                           # 5. a follow up
    if found:
        return respond(found, state, errors), "follow-up", found[-1][0], 1.0

    intent, confidence = classify(classifier, message)       # 6. the classifier
    if intent in HANDLERS and confidence >= THRESHOLD:
        ctx["fallbacks"] = 0
        ctx["last_intent"] = intent
        return safe_handle(intent, text, state, errors), "classifier", intent, confidence

    return fallback(state), "fallback", intent or "", confidence   # 7. the fallback
