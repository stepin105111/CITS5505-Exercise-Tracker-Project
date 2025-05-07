document.addEventListener("DOMContentLoaded", function () {
    // === PIE CHART: Workout Type Distribution ===
    const activitiesChart = document.getElementById("activitiesChart");
    if (activitiesChart) {
      const labels = JSON.parse(activitiesChart.dataset.labels || "[]");
      const data = JSON.parse(activitiesChart.dataset.counts || "[]");
  
      const activitiesCtx = activitiesChart.getContext("2d");
      const workoutTypeData = {
        labels: labels,
        datasets: [{
          label: 'Workout Types',
          data: data,
          backgroundColor: [
            '#3498db', '#e74c3c', '#2ecc71',
            '#f39c12', '#9b59b6', '#1abc9c'
          ],
        }]
      };
  
      new Chart(activitiesCtx, {
        type: 'pie',
        data: workoutTypeData,
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'right',
            },
            title: {
              display: true,
              text: 'Workout Type Distribution'
            }
          }
        }
      });
    }
  
    // === BAR CHART: Calories Burned per Weekday ===
    const weekdayChart = document.getElementById("weekdayChart");
    if (weekdayChart) {
      const weekdayLabels = JSON.parse(weekdayChart.dataset.labels || "[]");
      const weekdayValues = JSON.parse(weekdayChart.dataset.values || "[]");
  
      new Chart(weekdayChart.getContext("2d"), {
        type: 'bar',
        data: {
          labels: weekdayLabels,
          datasets: [{
            label: 'Calories Burned',
            data: weekdayValues,
            backgroundColor: '#f39c12',
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Calories Burned by Weekday'
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }
  
    // === LINE CHART: Time Spent per Weekday ===
    const timeChart = document.getElementById("timeChart");
    if (timeChart) {
      const timeLabels = JSON.parse(timeChart.dataset.labels || "[]");
      const timeValues = JSON.parse(timeChart.dataset.values || "[]");
  
      new Chart(timeChart.getContext("2d"), {
        type: 'line',
        data: {
          labels: timeLabels,
          datasets: [{
            label: 'Time Spent (minutes)',
            data: timeValues,
            borderColor: '#2ecc71',
            backgroundColor: 'rgba(46, 204, 113, 0.1)',
            tension: 0.3,
            fill: true,
            pointBackgroundColor: '#2ecc71',
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Time Spent on Workouts by Weekday'
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }
  
    // === PROGRESS BAR COLORING BASED ON % ===
    const progressBars = document.querySelectorAll(".progress-bar");
    progressBars.forEach(bar => {
      const value = parseFloat(bar.innerText.replace('%', '').trim());
  
      if (value >= 80) {
        bar.style.backgroundColor = '#2ecc71'; // green
      } else if (value >= 50) {
        bar.style.backgroundColor = '#f1c40f'; // yellow
      } else {
        bar.style.backgroundColor = '#e74c3c'; // red
      }
    });
  });
  