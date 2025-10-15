// SSL Referee Analysis Website JavaScript

// Sample data - in production this would be loaded from your analysis files
const sampleRefereeData = [
    {
        id: 3262,
        name: "Patric Terelius",
        matches: 4,
        penalties: 10,
        avgPenalties: 2.5,
        homeBias: 20.0,
        observations: [
            { type: "TIMING_PATTERN", severity: "MEDIUM", description: "Calls disproportionate number of penalties in final period (60.0%)" }
        ]
    },
    {
        id: 395,
        name: "Patrik Trofast", 
        matches: 5,
        penalties: 9,
        avgPenalties: 1.8,
        homeBias: 11.1,
        observations: [
            { type: "TIMING_PATTERN", severity: "MEDIUM", description: "Calls disproportionate number of penalties in final period (66.7%)" },
            { type: "PENALTY_TYPE_BIAS", severity: "LOW", description: "Shows strong preference for calling 'Fasthållning, 2 min' (44.4%)" }
        ]
    },
    {
        id: 3216,
        name: "Martin Jonsson",
        matches: 1,
        penalties: 5,
        avgPenalties: 5.0,
        homeBias: 20.0,
        observations: [
            { type: "PENALTY_RATE", severity: "MEDIUM", description: "Unusually strict referee - calls 5.0 penalties per match vs league average of 2.6" }
        ]
    },
    {
        id: 665,
        name: "Joakim Mattsson",
        matches: 1,
        penalties: 5,
        avgPenalties: 5.0,
        homeBias: 20.0,
        observations: [
            { type: "PENALTY_RATE", severity: "MEDIUM", description: "Unusually strict referee - calls 5.0 penalties per match" }
        ]
    },
    {
        id: 3225,
        name: "David Dornlöv",
        matches: 4,
        penalties: 6,
        avgPenalties: 1.5,
        homeBias: -33.3,
        observations: [
            { type: "HOME_AWAY_BIAS", severity: "MEDIUM", description: "Shows significant bias AGAINST away team - calls 15.3% more penalties than league average" }
        ]
    }
];

// Initialize charts when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    populateRefereesList();
    setupFilterButtons();
});

function initializeCharts() {
    // Home vs Away Penalty Distribution
    const homeAwayCtx = document.getElementById('homeAwayChart').getContext('2d');
    new Chart(homeAwayCtx, {
        type: 'doughnut',
        data: {
            labels: ['Home Team Penalties', 'Away Team Penalties'],
            datasets: [{
                data: [35, 37], // Based on your real data: 48.6% home
                backgroundColor: ['#ef4444', '#3b82f6'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Penalties by Period
    const periodCtx = document.getElementById('periodChart').getContext('2d');
    new Chart(periodCtx, {
        type: 'bar',
        data: {
            labels: ['Period 1', 'Period 2', 'Period 3'],
            datasets: [{
                label: 'Penalties Called',
                data: [20, 25, 27], // Estimated distribution
                backgroundColor: '#2563eb',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Most Common Penalty Types
    const penaltyTypesCtx = document.getElementById('penaltyTypesChart').getContext('2d');
    new Chart(penaltyTypesCtx, {
        type: 'horizontalBar',
        data: {
            labels: ['Fasthållning, 2 min', 'Hårt spel 2 min', 'Slag, 2 min', 'Felaktigt avstånd, 2 min', 'Otillåten trängning, 2 min'],
            datasets: [{
                label: 'Frequency',
                data: [15, 12, 10, 8, 6],
                backgroundColor: '#10b981',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });

    // Referee Penalty Rate Distribution
    const refereeRatesCtx = document.getElementById('refereeRatesChart').getContext('2d');
    new Chart(refereeRatesCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Referees',
                data: sampleRefereeData.map(ref => ({
                    x: ref.matches,
                    y: ref.avgPenalties,
                    referee: ref.name
                })),
                backgroundColor: '#f59e0b',
                borderColor: '#d97706',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Matches Officiated'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Average Penalties per Match'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.raw.referee}: ${context.raw.y} penalties/match (${context.raw.x} matches)`;
                        }
                    }
                }
            }
        }
    });
}

function populateRefereesList() {
    const refereesList = document.getElementById('referees-list');
    
    sampleRefereeData.forEach(referee => {
        const card = createRefereeCard(referee);
        refereesList.appendChild(card);
    });
}

function createRefereeCard(referee) {
    const card = document.createElement('div');
    card.className = 'referee-card';
    
    // Add classes based on referee characteristics
    if (referee.observations.length > 0) {
        card.classList.add('has-bias');
    }
    if (referee.avgPenalties > 3.5) {
        card.classList.add('strict');
    } else if (referee.avgPenalties < 2.0) {
        card.classList.add('lenient');
    }
    
    // Set data attributes for filtering
    card.dataset.filter = 'all';
    if (referee.observations.length > 0) card.dataset.filter += ' bias';
    if (referee.avgPenalties > 3.5) card.dataset.filter += ' strict';
    if (referee.avgPenalties < 2.0) card.dataset.filter += ' lenient';
    
    const biasColor = referee.homeBias > 15 ? '#ef4444' : 
                     referee.homeBias < -15 ? '#3b82f6' : '#10b981';
    
    card.innerHTML = `
        <div class="referee-header">
            <div>
                <div class="referee-name">${referee.name}</div>
                <div class="referee-id">ID: ${referee.id}</div>
            </div>
        </div>
        
        <div class="referee-stats">
            <div class="referee-stat">
                <span class="referee-stat-value">${referee.matches}</span>
                <span class="referee-stat-label">Matches</span>
            </div>
            <div class="referee-stat">
                <span class="referee-stat-value">${referee.avgPenalties.toFixed(1)}</span>
                <span class="referee-stat-label">Avg Penalties</span>
            </div>
            <div class="referee-stat">
                <span class="referee-stat-value" style="color: ${biasColor}">${referee.homeBias > 0 ? '+' : ''}${referee.homeBias.toFixed(1)}%</span>
                <span class="referee-stat-label">Home Bias</span>
            </div>
            <div class="referee-stat">
                <span class="referee-stat-value">${referee.penalties}</span>
                <span class="referee-stat-label">Total Penalties</span>
            </div>
        </div>
        
        ${referee.observations.length > 0 ? `
            <div class="referee-observations">
                ${referee.observations.map(obs => `
                    <div class="observation">
                        <strong>${getSeverityEmoji(obs.severity)} ${obs.severity}:</strong> ${obs.description}
                    </div>
                `).join('')}
            </div>
        ` : ''}
    `;
    
    return card;
}

function getSeverityEmoji(severity) {
    const emojis = {
        'LOW': '🟡',
        'MEDIUM': '🟠', 
        'HIGH': '🔴',
        'CRITICAL': '⚠️'
    };
    return emojis[severity] || '🔵';
}

function setupFilterButtons() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const refereeCards = document.querySelectorAll('.referee-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Filter cards
            const filter = button.dataset.filter;
            
            refereeCards.forEach(card => {
                if (filter === 'all' || card.dataset.filter.includes(filter)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

function downloadData() {
    // In production, this would download the actual CSV files
    alert('Data download feature coming soon! For now, visit the GitHub repository to access the raw data files.');
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading animation
window.addEventListener('load', function() {
    document.body.classList.add('loaded');
});