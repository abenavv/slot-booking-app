from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
#for frontend backend connection shitties
from datetime import date,timedelta
#timedelta is like delta function diffrnce kittan

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#react runs on port 5173 backend runs on 8000 so CORS allows 5173 to make reqsts on 8000

class Facility(BaseModel):
    id: int
    name: str
    
bookings = []
next_booking_id = 1
    
facilities = [
    Facility(id=1, name="Badminton Court 1"),
    Facility(id=2, name="Badminton Court 2"),
    Facility(id=3, name="Tennis Court"),
] #facilites is a list of facility classes

@app.get("/health")
def health():
    return {"status": "ok"}


# 1. List the 3 facilities(pydantic modal this too)
@app.get("/facilities")
def get_facilities():
    return [facility.model_dump() for facility in facilities]


# 2. Slots for a facility on a date
@app.get("/slots")
def get_slots(facility_id: int, date_str: str):
    try:
        date.fromisoformat(date_str)
        #checking if its a valid date ie if conversion to py readabel form is possible then its gud
    except ValueError:
        return { "message": "Invalid date format. Use YYYY-MM-DD" }
    #just validated the date entering here as in correct format    
    hours=range(6, 22)  # 6 AM to 11 PM.last slot 9-10
    slots=[]
    for hour in hours:
        #availablity also shows here now
        is_booked=any(
            existing_booking["facility_id"]==facility_id
            #booking not yet came we have start hr(hour),facility_id and date with us
            and existing_booking["date"]==date_str
            and existing_booking["start_time"]==f"{hour:02d}:00"
            for existing_booking in bookings
        )
        #any means ethenkilum oralk in those loop of existing bookings true ano enn nokm
        #if yes is_booked=true varum
        slot={
            "start_time": f"{hour:02d}:00", #make hr 6 to 06:00
            "end_time": f"{hour+1:02d}:00",
            "status": "booked" if is_booked else "available"
            }
        slots.append(slot)
    
    return slots


# 3. Create a booking
class BookingRequest(BaseModel): #basemodel is another pydantic class 
    #BR inherits it kinda
    member_id: int
    facility_id: int
    date: str
    start_time: str


@app.post("/bookings")
def create_booking(booking: BookingRequest):
    #the function is called only if it passes pydantic checks
    #ie if the details are in correct form(no missing details)
    #ie if it passes booking object comes in to play
    #so booking.facility_id or anything of booking.something is already known
    #so that check is possible before creating new_booking guy   
    global next_booking_id #to access/modfy the variable outside a fn
    
    #facility invalid case
    if booking.facility_id not in [facility.id for facility in facilities]:
        return { "message": "Invalid facility" }
    
    #date<=7days or date already passed?
    
    try:
        today = date.today()
        booking_date = date.fromisoformat(booking.date) #make the dates to python readable form
        #the day when we wish to book for
        last_date = today + timedelta(days=7)
        
        if booking_date>last_date or booking_date<today:
            return { "message": "Date is outside the booking window" }
    
    #this if for if the date is enetered in wrong format like "tmrw" or indian kinda dates
    #it generates value error
    except ValueError:
        return { "message": "Invalid date format. Use YYYY-MM-DD" }
    
    #valid time slot or not
        
    valid_times = [f"{hour:02d}:00" for hour in range(6, 22)]
    #v_t gives 6:00 to 21:00
    if booking.start_time not in valid_times:
        return {"message" : "Please enter a valid start time"}
            
               
    #prevent double bookings
    
    for existing_booking in bookings:
        if(existing_booking["facility_id"]==booking.facility_id
            and existing_booking["date"]==booking.date
            and existing_booking["start_time"]==booking.start_time
            ):
            return {"message" : "Sorry , Slot already booked"}
        
    
    #maximum 3 active bookings
    
    active_count=0
    
    for existing_booking in bookings:
        if(existing_booking["member_id"]==booking.member_id
           and date.fromisoformat(existing_booking["date"])>=today
           ):
            active_count+=1
            
    if active_count>=3:
        return {"message" : "Sorry , You already have three active bookings"}

    #validate 1st save scnd
    
    new_booking = {
        "id": next_booking_id,
        "member_id": booking.member_id, #booking is like self here
        "facility_id": booking.facility_id,
        "date": booking.date,
        "start_time": booking.start_time,
    }
    
    bookings.append(new_booking)
    next_booking_id += 1

    return {
        "message": "Booking confirmed",
        "booking": new_booking,
    }



# 4. A member's active bookings

@app.get("/bookings")
def get_member_bookings(member_id: int):
    return [
        booking for booking in bookings
        if booking["member_id"] == member_id
    ]
