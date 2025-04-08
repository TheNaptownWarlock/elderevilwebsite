document.addEventListener('DOMContentLoaded', function() {
    const blogPosts = document.querySelectorAll('.blog-post');
    const blogSection = document.getElementById('blog');

    blogPosts.forEach(post => {
        const readMoreLink = post.querySelector('.read-more');
        if (readMoreLink) {
            readMoreLink.addEventListener('click', function(e) {
                e.preventDefault();
                const postTitle = post.querySelector('h3').textContent;
                const postDate = post.querySelector('.blog-date').textContent;
                const postContent = post.querySelector('p:not(.blog-date)').textContent;

                // Create and show the full blog post
                const fullPost = document.createElement('div');
                fullPost.className = 'full-blog-post';
                fullPost.innerHTML = `
                    <h3>${postTitle}</h3>
                    <p class="blog-date">${postDate}</p>
                    <div class="blog-content">
                        <p>${postContent}</p>
                    </div>
                    <button class="close-blog-post glow-button">Close</button>
                `;

                // Remove any existing full post
                const existingPost = blogSection.querySelector('.full-blog-post');
                if (existingPost) {
                    existingPost.remove();
                }

                blogSection.appendChild(fullPost);
                fullPost.scrollIntoView({ behavior: 'smooth' });

                // Add close button functionality
                const closeButton = fullPost.querySelector('.close-blog-post');
                closeButton.addEventListener('click', function() {
                    fullPost.remove();
                });
            });
        }
    });
}); 