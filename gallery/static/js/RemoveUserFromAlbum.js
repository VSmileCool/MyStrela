function removeUser(userEmail, albumId) {
  const url = `/delete-user-from-album/?user_email=${encodeURIComponent(userEmail)}&album_id=${encodeURIComponent(albumId)}`;

  const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  fetch(url, {
    method: "DELETE", // Используйте 'POST' или 'GET' в зависимости от ваших требований
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      location.reload();
    })
    .catch((error) => {
      console.error(error);
      location.reload();
    });
}
