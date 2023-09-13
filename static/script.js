function formatTimestamp(timestamp) {
    const now = new Date();
    const targetTime = new Date(timestamp);

    // Calculate the time difference in milliseconds
    const timeDiff = now - targetTime;

    if (timeDiff < 60000) {
        // Less than 1 minute ago
        return "now";
    } else if (timeDiff < 3600000) {
        // Less than 1 hour ago
        const minutesAgo = Math.floor(timeDiff / 60000);
        return `${minutesAgo} minute${minutesAgo !== 1 ? 's' : ''} ago`;
    } else if (timeDiff < 86400000) {
        // Less than 24 hours ago
        const hoursAgo = Math.floor(timeDiff / 3600000);
        return `${hoursAgo} hour${hoursAgo !== 1 ? 's' : ''} ago`;
    } else {
        // More than 1 day ago
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return targetTime.toLocaleDateString(undefined, options);
    }
}


function calculateReadingTime(text) {
    // Define the average reading speed (words per minute)
    const wordsPerMinute = 200; // Adjust this value as needed

    // Calculate the number of words in the text
    const wordCount = text.split(/\s+/).length;

    // Calculate the reading time in minutes
    const readingTimeMinutes = Math.ceil(wordCount / wordsPerMinute);

    // Create a formatted string
    const readingTimeText = `${readingTimeMinutes} min read`;

    return readingTimeText;
}