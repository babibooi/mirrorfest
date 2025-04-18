async function loadThreads() {
  try {
    const res = await fetch("/api/threads");
    if (!res.ok) throw new Error("Failed to load threads");
    const threads = await res.json();
    console.log("Loaded threads:", threads);
    renderForum(threads);
  } catch (err) {
    console.error(err);
    const forumEl = document.getElementById("forum");
    forumEl.innerHTML = "<p>Error loading threads.</p>";
  }
}

async function createThread() {
  const user = document.getElementById("username").value || "Unknown";
  const title = document.getElementById("threadTitle").value;
  const body = document.getElementById("threadBody").value;
  if (!title || !body) return alert("Please enter thread title and message.");
  try {
    const res = await fetch("/api/threads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user, title, message: body })
    });
    if (!res.ok) throw new Error("Failed to create thread");
    const newThread = await res.json();
    loadThreads();
    document.getElementById("threadTitle").value = "";
    document.getElementById("threadBody").value = "";
  } catch (err) {
    console.error(err);
    alert("Error creating thread.");
  }
}

async function deleteThread(threadId) {
  if (!confirm("Are you sure you want to delete this thread?")) return;
  try {
    const res = await fetch(`/api/threads/${threadId}`, {
      method: "DELETE"
    });
    if (!res.ok) throw new Error("Failed to delete thread");
    loadThreads();
  } catch (err) {
    console.error(err);
    alert("Error deleting thread.");
  }
}
