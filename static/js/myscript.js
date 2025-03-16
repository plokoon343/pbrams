document.getElementById('allocation-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const name = document.getElementById('name').value;
    const priority = document.getElementById('priority').value;

    // Create a new list item for the allocated room
    const li = document.createElement('li');
    li.textContent = `Name: ${name}, Priority: ${priority}`;
    
    // Insert the item based on priority
    const list = document.getElementById('allocated-rooms');
    if (priority === 'high') {
        list.prepend(li); // High-priority at the top
    } else if (priority === 'medium') {
        const mediumItems = Array.from(list.children).filter(item => item.textContent.includes('Medium'));
        if (mediumItems.length > 0) {
            mediumItems[mediumItems.length - 1].after(li);
        } else {
            list.appendChild(li);
        }
    } else {
        list.appendChild(li); // Low-priority at the bottom
    }

    // Clear the form
    document.getElementById('name').value = '';
});
