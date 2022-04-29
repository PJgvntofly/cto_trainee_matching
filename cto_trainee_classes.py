#Create classes for CTO-Trainee Matching application

class Employee:
    def __init__(self, firstName, lastName, shift, schedule, callTaking, police, fire, personality):
        self.firstName = firstName
        self.lastName = lastName
        self.shift = shift
        self.schedule = schedule
        self.calltaking = callTaking
        self.police = police
        self.fire = fire
        self.personality = personality
    def updateShift(self, newShift):
        self.shift = newShift
    def updateSchedule(self, newSchedule):
        self.schedule = newSchedule
    def updateDisciplines(self, policeUpdate, fireUpdate):
        if self.police != policeUpdate:
            self.police == policeUpdate
        if self.fire != fireUpdate:
            self.fire = fireUpdate

class CTO(Employee):
    def __init__(self, firstName, lastName, shift, schedule, callTaking, police, fire, personality, partTime, skill, onBreak):
        super().__init__(firstName, lastName, shift, schedule, callTaking, police, fire, personality)
        self.partTime = partTime
        self.skill = skill
        self.onBreak = onBreak
    def toggleBreak(self):
        if self.onBreak == 1:
            self.onBreak = 0
        else:
            self.onBreak = 1
    def updateSkill(self, newSkill):
        self.skill = newSkill

class Trainee(Employee):
    def __init__(self, firstName, lastName, shift, schedule, callTaking, police, fire, personality, minSkill):
        super().__init__(firstName, lastName, shift, schedule, callTaking, police, fire, personality)
        self.minSkill = minSkill
    def updateMinSkill(self, newMinSkill):
        self.minSkill = newMinSkill

