async function addReply(threadId) {
  const user = document.getElementById("username").value || "Unknown";
  const replyText = document.getElementById(`reply-${threadId}`).value;
  if (!replyText) return alert("Please enter a reply.");
  try {
    const res = await fetch(`/api/threads/${threadId}/posts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user, message: replyText })
    });
    if (!res.ok) throw new Error("Failed to add reply");
    const newPost = await res.json();
    loadThreads();
    document.getElementById(`reply-${threadId}`).value = "";
  } catch (err) {
    console.error(err);
    alert("Error adding reply.");
  }
}

async function deletePost(threadId, postIndex) {
  if (!confirm("Are you sure you want to delete this post?")) return;
  try {
    const res = await fetch(`/api/threads/${threadId}/posts/${postIndex}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Failed to delete post");
    loadThreads();
  } catch (err) {
    console.error(err);
    alert("Error deleting post.");
  }
}
