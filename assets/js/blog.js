document.addEventListener('DOMContentLoaded', function() {
    const blogPosts = document.querySelectorAll('.blog-post');
    const blogSection = document.getElementById('blog');

    blogPosts.forEach(post => {
        const readMoreLink = post.querySelector('.read-more');
        if (readMoreLink) {
            readMoreLink.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Toggle between preview and full content
                const previewContent = post.querySelector('.preview-content');
                const fullContent = post.querySelector('.full-content');
                
                if (previewContent.style.display !== 'none') {
                    // Show full content
                    previewContent.style.display = 'none';
                    fullContent.style.display = 'block';
                    readMoreLink.textContent = 'Show Less';
                    
                    // Scroll to the post
                    post.scrollIntoView({ behavior: 'smooth', block: 'start' });
                } else {
                    // Show preview content
                    previewContent.style.display = 'block';
                    fullContent.style.display = 'none';
                    readMoreLink.textContent = 'Read More';
                }
            });
        }
    });
}); 