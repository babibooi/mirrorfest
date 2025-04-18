const forumEl = document.getElementById("forum");

function renderForum(threads) {
  console.log("Rendering forum with threads:", threads);
  forumEl.innerHTML = "";
  threads.forEach((thread) => {
    console.log("Rendering thread:", thread.title);
    const div = document.createElement("div");
    div.className = "thread";

    // Create collapsible header with summary info
    const header = document.createElement("h3");
    header.style.cursor = "pointer";

    // Format date/time for first post and last post
    const firstPost = thread.posts[0];
    const lastPost = thread.posts[thread.posts.length - 1];
    const firstTimestamp = new Date(firstPost.timestamp).toLocaleString();
    const lastTimestamp = new Date(lastPost.timestamp).toLocaleString();

    // Summary text: title, first post date/time, first message snippet, number of replies, last reply date/time
    const summaryText = `${thread.title} | Started: ${firstTimestamp} | First message: "${firstPost.message.substring(0, 50)}${firstPost.message.length > 50 ? '...' : ''}" | Replies: ${thread.posts.length - 1} | Last reply: ${lastTimestamp}`;

    header.textContent = summaryText + " ";

    header.onclick = () => {
      const content = div.querySelector(".thread-content");
      if (content.style.display === "none") {
        content.style.display = "block";
      } else {
        content.style.display = "none";
      }
    };

    // Delete thread button
    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "[Delete Thread]";
    deleteBtn.style.color = "red";
    deleteBtn.onclick = (e) => {
      e.stopPropagation();
      deleteThread(thread.id);
    };
    header.appendChild(deleteBtn);
    div.appendChild(header);

    // Start with thread content collapsed by default
    const contentDiv = document.createElement("div");
    contentDiv.className = "thread-content";
    contentDiv.style.display = "none";

    // Add posts
    thread.posts.forEach((p, postIndex) => {
      const postDiv = document.createElement("div");
      postDiv.className = "post";

      // Post content
      const postContent = document.createElement("span");
      postContent.innerHTML = `<strong>${p.user}</strong>: ${p.message} <span class="timestamp">[${p.timestamp}]</span>`;
      postDiv.appendChild(postContent);

      // Reactions container
      const reactionsDiv = document.createElement("div");
      reactionsDiv.className = "reactions";

      // Render existing reactions
      if (p.reactions) {
        for (const [reaction, users] of Object.entries(p.reactions)) {
          const reactionBtn = document.createElement("button");
          reactionBtn.textContent = `${reaction} ${users.length}`;
          reactionBtn.title = users.join(", ");
          reactionBtn.onclick = async (e) => {
            e.stopPropagation();
            const user = document.getElementById("username").value || "Unknown";
            if (users.includes(user)) {
              // Remove reaction
              await removeReaction(thread.id, postIndex, user, reaction);
            } else {
              // Add reaction
              await addReaction(thread.id, postIndex, user, reaction);
            }
            loadThreads();
          };
          reactionsDiv.appendChild(reactionBtn);
        }
      }

      // Add reaction input
      const reactionInput = document.createElement("input");
      reactionInput.type = "text";
      reactionInput.placeholder = "Add reaction (emoji)";
      reactionInput.maxLength = 2;
      reactionInput.style.width = "3em";
      reactionInput.onkeydown = async (e) => {
        if (e.key === "Enter") {
          const user = document.getElementById("username").value || "Unknown";
          const reaction = reactionInput.value.trim();
          if (reaction) {
            await addReaction(thread.id, postIndex, user, reaction);
            reactionInput.value = "";
            loadThreads();
          }
        }
      };
      reactionsDiv.appendChild(reactionInput);

      // Add common reaction buttons
      const commonReactions = ["👍", "❤️", "😂", "😮", "😢", "👏"];
      commonReactions.forEach((emoji) => {
        const btn = document.createElement("button");
        btn.textContent = emoji;
        btn.title = "Add/remove reaction";
        btn.style.marginLeft = "0.2em";
        btn.onclick = async (e) => {
          e.stopPropagation();
          const user = document.getElementById("username").value || "Unknown";
          const postReactions = p.reactions || {};
          const usersReacted = postReactions[emoji] || [];
          if (usersReacted.includes(user)) {
            await removeReaction(thread.id, postIndex, user, emoji);
          } else {
            await addReaction(thread.id, postIndex, user, emoji);
          }
          loadThreads();
        };
        reactionsDiv.appendChild(btn);
      });

      postDiv.appendChild(reactionsDiv);

      // Delete post button
      const delPostBtn = document.createElement("button");
      delPostBtn.textContent = "[Delete]";
      delPostBtn.style.color = "red";
      delPostBtn.onclick = (e) => {
        e.stopPropagation();
        deletePost(thread.id, postIndex);
      };
      postDiv.appendChild(delPostBtn);

      contentDiv.appendChild(postDiv);
    });

    // Reply textarea and button
    const replyTextarea = document.createElement("textarea");
    replyTextarea.id = `reply-${thread.id}`;
    replyTextarea.rows = 2;
    replyTextarea.placeholder = "Add reply...";
    contentDiv.appendChild(replyTextarea);
    contentDiv.appendChild(document.createElement("br"));

    const replyBtn = document.createElement("button");
    replyBtn.textContent = "Post Reply";
    replyBtn.onclick = () => addReply(thread.id);
    contentDiv.appendChild(replyBtn);

    div.appendChild(contentDiv);

    forumEl.appendChild(div);
  });
}
