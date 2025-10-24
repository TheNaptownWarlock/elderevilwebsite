// Fantasy Calendar RSVP JavaScript
class FantasyCalendar {
    constructor() {
        this.currentDate = new Date();
        this.selectedDate = null;
        this.events = JSON.parse(localStorage.getItem('fantasy-events') || '{}');
        this.rsvps = JSON.parse(localStorage.getItem('fantasy-rsvps') || '{}');
        this.activities = JSON.parse(localStorage.getItem('fantasy-activities') || '[]');
        
        this.init();
    }

    init() {
        this.renderCalendar();
        this.bindEvents();
        this.updateRSVPList();
        this.updateActivityList();
    }

    bindEvents() {
        document.getElementById('prevMonth').addEventListener('click', () => this.previousMonth());
        document.getElementById('nextMonth').addEventListener('click', () => this.nextMonth());
        document.getElementById('addEvent').addEventListener('click', () => this.addEvent());
        
        // Enter key support for form
        document.getElementById('eventTitle').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addEvent();
        });
    }

    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.renderCalendar();
    }

    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.renderCalendar();
    }

    renderCalendar() {
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

        document.getElementById('currentMonth').textContent = 
            `${monthNames[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;

        const grid = document.getElementById('calendarGrid');
        grid.innerHTML = '';

        // Add day headers
        dayNames.forEach(day => {
            const dayHeader = document.createElement('div');
            dayHeader.className = 'day-header';
            dayHeader.textContent = day;
            grid.appendChild(dayHeader);
        });

        // Get first day of month and number of days
        const firstDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
        const lastDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0);
        const today = new Date();

        // Add empty cells for days before month starts
        for (let i = 0; i < firstDay.getDay(); i++) {
            const emptyDay = document.createElement('div');
            emptyDay.className = 'calendar-day other-month';
            grid.appendChild(emptyDay);
        }

        // Add days of the month
        for (let day = 1; day <= lastDay.getDate(); day++) {
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            dayElement.textContent = day;
            
            const dateString = this.formatDate(new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), day));
            
            // Check if today
            const dayDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), day);
            if (this.isSameDate(dayDate, today)) {
                dayElement.classList.add('today');
            }
            
            // Check if has events
            if (this.events[dateString]) {
                dayElement.classList.add('has-event');
            }
            
            // Click handler
            dayElement.addEventListener('click', () => this.selectDate(dateString));
            
            grid.appendChild(dayElement);
        }
    }

    selectDate(dateString) {
        // Remove previous selection
        document.querySelectorAll('.calendar-day.selected').forEach(day => {
            day.classList.remove('selected');
        });
        
        // Add selection to clicked day
        event.target.classList.add('selected');
        
        this.selectedDate = dateString;
        this.displayEventDetails(dateString);
    }

    formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    isSameDate(date1, date2) {
        return date1.getDate() === date2.getDate() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getFullYear() === date2.getFullYear();
    }

    addEvent() {
        const title = document.getElementById('eventTitle').value.trim();
        const date = document.getElementById('eventDate').value;
        const time = document.getElementById('eventTime').value;
        const description = document.getElementById('eventDescription').value.trim();

        if (!title || !date || !time) {
            alert('🧙‍♂️ Please fill in all required fields for your quest!');
            return;
        }

        if (!this.events[date]) {
            this.events[date] = [];
        }

        const event = {
            id: Date.now(),
            title,
            time,
            description,
            creator: 'The Naptown Warlock'
        };

        this.events[date].push(event);
        this.saveData();
        
        // Add to activity log
        this.addActivity(`⚔️ New quest created: "${title}" on ${this.formatDateDisplay(date)}`);

        // Clear form
        document.getElementById('eventTitle').value = '';
        document.getElementById('eventDate').value = '';
        document.getElementById('eventTime').value = '';
        document.getElementById('eventDescription').value = '';

        this.renderCalendar();
        
        if (this.selectedDate === date) {
            this.displayEventDetails(date);
        }
    }

    displayEventDetails(dateString) {
        const titleElement = document.getElementById('selectedDateTitle');
        const detailsElement = document.getElementById('eventDetails');
        
        titleElement.textContent = `🗓️ ${this.formatDateDisplay(dateString)}`;
        
        if (!this.events[dateString] || this.events[dateString].length === 0) {
            detailsElement.innerHTML = '<p>No quests planned for this day.</p>';
            return;
        }

        let html = '';
        this.events[dateString].forEach(event => {
            const rsvpKey = `${dateString}-${event.id}`;
            const eventRSVPs = this.rsvps[rsvpKey] || [];
            
            html += `
                <div class="event-item">
                    <div class="event-title">⚔️ ${event.title}</div>
                    <div class="event-time">🕐 ${event.time}</div>
                    ${event.description ? `<div class="event-description">${event.description}</div>` : ''}
                    
                    <div class="rsvp-controls">
                        <input type="text" class="name-input" placeholder="Your name" id="name-${event.id}">
                        <button class="rsvp-btn rsvp-yes" onclick="calendar.addRSVP('${rsvpKey}', '${event.id}', 'yes')">
                            🗡️ Going!
                        </button>
                        <button class="rsvp-btn rsvp-maybe" onclick="calendar.addRSVP('${rsvpKey}', '${event.id}', 'maybe')">
                            🤔 Maybe
                        </button>
                        <button class="rsvp-btn rsvp-no" onclick="calendar.addRSVP('${rsvpKey}', '${event.id}', 'no')">
                            ❌ Can't make it
                        </button>
                    </div>
                    
                    ${eventRSVPs.length > 0 ? `
                        <div class="event-rsvps">
                            <h4>⚔️ Adventurers:</h4>
                            ${eventRSVPs.map(rsvp => `
                                <span class="rsvp-status ${rsvp.status}">${rsvp.name}</span>
                            `).join(' ')}
                        </div>
                    ` : ''}
                </div>
            `;
        });
        
        detailsElement.innerHTML = html;
    }

    addRSVP(rsvpKey, eventId, status) {
        const nameInput = document.getElementById(`name-${eventId}`);
        const name = nameInput.value.trim();
        
        if (!name) {
            alert('🧙‍♂️ Please enter your name, brave adventurer!');
            return;
        }

        if (!this.rsvps[rsvpKey]) {
            this.rsvps[rsvpKey] = [];
        }

        // Remove existing RSVP from same person
        this.rsvps[rsvpKey] = this.rsvps[rsvpKey].filter(rsvp => rsvp.name !== name);
        
        // Add new RSVP
        this.rsvps[rsvpKey].push({
            name,
            status,
            timestamp: new Date().toISOString()
        });

        this.saveData();
        
        // Add to activity
        const statusEmoji = status === 'yes' ? '✅' : status === 'maybe' ? '🤔' : '❌';
        this.addActivity(`${statusEmoji} ${name} RSVPed "${status}" for ${this.selectedDate}`);
        
        // Clear name input
        nameInput.value = '';
        
        // Refresh display
        this.displayEventDetails(this.selectedDate);
        this.updateRSVPList();
    }

    updateRSVPList() {
        const listElement = document.getElementById('rsvpList');
        let html = '';

        // Get all RSVPs and sort by date
        const allRSVPs = [];
        Object.keys(this.rsvps).forEach(rsvpKey => {
            const [dateString, eventId] = rsvpKey.split('-');
            const event = this.events[dateString]?.find(e => e.id == eventId);
            
            if (event) {
                this.rsvps[rsvpKey].forEach(rsvp => {
                    allRSVPs.push({
                        ...rsvp,
                        eventTitle: event.title,
                        date: dateString,
                        eventId
                    });
                });
            }
        });

        // Sort by date (newest first)
        allRSVPs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        if (allRSVPs.length === 0) {
            html = '<p>No RSVPs yet. Be the first to join a quest! ⚔️</p>';
        } else {
            allRSVPs.slice(0, 10).forEach(rsvp => { // Show last 10
                const statusEmoji = rsvp.status === 'yes' ? '🗡️' : rsvp.status === 'maybe' ? '🤔' : '❌';
                html += `
                    <div class="rsvp-item">
                        <div>
                            <strong>${rsvp.name}</strong> ${statusEmoji} 
                            <em>${rsvp.eventTitle}</em>
                            <br><small>📅 ${this.formatDateDisplay(rsvp.date)}</small>
                        </div>
                        <span class="rsvp-status ${rsvp.status}">${rsvp.status.toUpperCase()}</span>
                    </div>
                `;
            });
        }

        listElement.innerHTML = html;
    }

    updateActivityList() {
        const listElement = document.getElementById('recentActivity');
        
        if (this.activities.length === 0) {
            listElement.innerHTML = '<p>No recent activity. Create your first quest! 🏰</p>';
            return;
        }

        const html = this.activities
            .slice(-10) // Show last 10 activities
            .reverse() // Newest first
            .map(activity => `
                <div class="activity-item">
                    <span>${activity.message}</span>
                    <small>${new Date(activity.timestamp).toLocaleString()}</small>
                </div>
            `).join('');

        listElement.innerHTML = html;
    }

    addActivity(message) {
        this.activities.push({
            message,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 50 activities
        if (this.activities.length > 50) {
            this.activities = this.activities.slice(-50);
        }
        
        this.saveData();
        this.updateActivityList();
    }

    formatDateDisplay(dateString) {
        const date = new Date(dateString + 'T00:00:00');
        return date.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    }

    saveData() {
        localStorage.setItem('fantasy-events', JSON.stringify(this.events));
        localStorage.setItem('fantasy-rsvps', JSON.stringify(this.rsvps));
        localStorage.setItem('fantasy-activities', JSON.stringify(this.activities));
    }
}

// Initialize the calendar when page loads
let calendar;
document.addEventListener('DOMContentLoaded', () => {
    calendar = new FantasyCalendar();
});

// Add some sample data if none exists
document.addEventListener('DOMContentLoaded', () => {
    const hasData = localStorage.getItem('fantasy-events');
    
    if (!hasData) {
        // Add sample event for today + 7 days
        const sampleDate = new Date();
        sampleDate.setDate(sampleDate.getDate() + 7);
        const dateString = sampleDate.toISOString().split('T')[0];
        
        const sampleEvents = {
            [dateString]: [{
                id: Date.now(),
                title: "Epic D&D Campaign Kickoff",
                time: "19:00",
                description: "Join us for the beginning of our new campaign! Bring dice, snacks, and your sense of adventure!",
                creator: "The Naptown Warlock"
            }]
        };
        
        localStorage.setItem('fantasy-events', JSON.stringify(sampleEvents));
        
        // Refresh calendar to show sample data
        setTimeout(() => {
            if (calendar) {
                calendar.events = sampleEvents;
                calendar.renderCalendar();
            }
        }, 100);
    }
});