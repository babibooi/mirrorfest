async function addReaction(threadId, postIndex, user, reaction) {
  try {
    const res = await fetch(`/api/threads/${threadId}/posts/${postIndex}/reactions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user, reaction })
    });
    if (!res.ok) throw new Error("Failed to add reaction");
    return await res.json();
  } catch (err) {
    console.error(err);
    alert("Error adding reaction.");
  }
}

async function removeReaction(threadId, postIndex, user, reaction) {
  try {
    const res = await fetch(`/api/threads/${threadId}/posts/${postIndex}/reactions`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user, reaction })
    });
    if (!res.ok) throw new Error("Failed to remove reaction");
    return await res.json();
  } catch (err) {
    console.error(err);
    alert("Error removing reaction.");
  }
}
