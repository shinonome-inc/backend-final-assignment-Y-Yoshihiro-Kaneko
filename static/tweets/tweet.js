const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

const likeCounters = document.querySelectorAll("#tweet-like-counter");
const toggleLikeBtns = document.querySelectorAll("#tweet-toggle-like-btn");

for (const btn of toggleLikeBtns) {
	btn.addEventListener("click", async (event) => {
		const btn = event.target;
		const pk = btn.dataset.tweetPk;
		const sendLike = btn.dataset.isLikeTweet.trim() === "false";
		const url = `/tweets/${pk}/${sendLike ? "like" : "unlike"}/`;

		try {
			const response = await fetch(url, {
				method: "POST",
				headers: { "X-CSRFToken": csrftoken },
			});
			if (!response.ok) {
				console.error(await response.json());
				return;
			}
		} catch (error) {
			console.error(error.message);
			return;
		}

		const likeCounter = Array(...likeCounters).find(
			(e) => e.dataset.tweetPk === pk,
		);
		const likeCount = Number.parseInt(likeCounter.innerText);
		likeCounter.innerText = sendLike ? likeCount + 1 : likeCount - 1;

		btn.dataset.isLikeTweet = sendLike ? "true" : "false";
		btn.innerText = sendLike ? "いいねを取り消す" : "いいねする";
	});
}
