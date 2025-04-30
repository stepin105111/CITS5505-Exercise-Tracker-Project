/**
 * Friend search and management functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('user-search');
    const searchResults = document.getElementById('search-results');
    
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
                      `<button class="remove-btn" data-username="${user.username}">Remove Friend</button>` : 
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
              
              document.querySelectorAll('.remove-btn').forEach(btn => {
                btn.addEventListener('click', removeFriend);
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
            // Change button to "Remove Friend"
            e.target.className = 'remove-btn';
            e.target.textContent = 'Remove Friend';
            e.target.removeEventListener('click', addFriend);
            e.target.addEventListener('click', removeFriend);
            
            // Show success message
            alert(`Added ${username} as a friend!`);
            
            // Reload the page to show updated friend list
            setTimeout(() => {
              window.location.reload();
            }, 1000);
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
            // Change button to "Add Friend"
            e.target.className = 'add-btn';
            e.target.textContent = 'Add Friend';
            e.target.removeEventListener('click', removeFriend);
            e.target.addEventListener('click', addFriend);
            
            // Show success message
            alert(`Removed ${username} from friends.`);
            
            // Reload the page to show updated friend list
            setTimeout(() => {
              window.location.reload();
            }, 1000);
          }
        })
        .catch(error => {
          console.error('Error removing friend:', error);
          alert('Error removing friend. Please try again.');
        });
    }
  });