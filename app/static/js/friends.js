/**
 * Friend search and management functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('user-search');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput || !searchResults) {
      return; // Exit if elements not found (not on friends tab)
    }
    
    let searchTimeout;
    
    // Search for users as the user types
    searchInput.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      
      const query = this.value.trim();
      
      if (query.length < 2) {
        searchResults.innerHTML = '';
        return;
      }
      
      searchTimeout = setTimeout(() => {
        fetch(`/search-users?query=${encodeURIComponent(query)}`)
          .then(response => response.json())
          .then(data => {
            searchResults.innerHTML = '';
            
            if (data.users && data.users.length > 0) {
              data.users.forEach(user => {
                const userCard = document.createElement('div');
                userCard.className = 'user-card';
                userCard.innerHTML = `
                  <div class="user-info">
                    <strong>${user.username}</strong>
                  </div>
                  <div>
                    ${user.is_friend ? 
                      `<span class="friend-badge">Already Friends</span>` : 
                      `<button class="add-btn" data-username="${user.username}">Add Friend</button>`
                    }
                  </div>
                `;
                searchResults.appendChild(userCard);
              });
              
              // Add event listeners to the new buttons
              document.querySelectorAll('.add-btn').forEach(btn => {
                btn.addEventListener('click', addFriend);
              });
              
            } else {
              searchResults.innerHTML = '<p class="text-center">No users found</p>';
            }
          })
          .catch(error => {
            console.error('Error searching users:', error);
            searchResults.innerHTML = '<p class="text-center text-danger">Error searching for users</p>';
          });
      }, 500);
    });
    
    // Function to refresh share section and clear search
    function refreshShareSectionAndClearSearch() {
      // Clear search input and results
      searchInput.value = '';
      searchResults.innerHTML = '';
      
      // Refresh the leaderboard content
      fetch(window.location.href)
        .then(response => response.text())
        .then(html => {
          // Create a temporary element to parse the HTML
          const tempDiv = document.createElement('div');
          tempDiv.innerHTML = html;
          
          // Get the updated share section
          const newShareSection = tempDiv.querySelector('#share-section');
          const currentShareSection = document.getElementById('share-section');
          
          if (newShareSection && currentShareSection) {
            // Replace just the inner content of the leaderboard
            const leaderboardContainer = newShareSection.querySelector('.leaderboard-container');
            const currentLeaderboardContainer = currentShareSection.querySelector('.leaderboard-container');
            
            if (leaderboardContainer && currentLeaderboardContainer) {
              currentLeaderboardContainer.innerHTML = leaderboardContainer.innerHTML;
              attachRemoveListeners();
            }
          }
        })
        .catch(error => {
          console.error('Error refreshing share section:', error);
        });
    }
    
    // Add friend function
    function addFriend(e) {
      const username = e.target.dataset.username;
      
      fetch('/add-friend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username }),
      })
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            alert(data.error);
          } else {
            // Show success message
            alert(`Added ${username} as a friend!`);
            
            // Refresh section and clear search
            refreshShareSectionAndClearSearch();
          }
        })
        .catch(error => {
          console.error('Error adding friend:', error);
          alert('Error adding friend. Please try again.');
        });
    }
    
    // Remove friend function
    function removeFriend(e) {
      const username = e.target.dataset.username;
      
      fetch('/remove-friend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username }),
      })
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            alert(data.error);
          } else {
            // Show success message
            alert(`Removed ${username} from friends.`);
            
            // Refresh section and clear search
            refreshShareSectionAndClearSearch();
          }
        })
        .catch(error => {
          console.error('Error removing friend:', error);
          alert('Error removing friend. Please try again.');
        });
    }

    // Function to attach event listeners to remove buttons in the leaderboard
    function attachRemoveListeners() {
      document.querySelectorAll('.friend-card .remove-btn').forEach(btn => {
        btn.addEventListener('click', removeFriend);
      });
    }

    attachRemoveListeners();
  });