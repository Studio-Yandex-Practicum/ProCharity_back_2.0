function view_query_parameters(destElementSelector) {
  const destElement = document.querySelector(destElementSelector);
  if (destElement) {
    const searchParams = new URL(document.location).searchParams;
    let paramsObject = {};

    for (const [key, value] of searchParams) {
      paramsObject[key] = value;
    }

    fetch(`${paramsObject.api_root_path}/task/${paramsObject.id}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Задание неактуально");
        }
        return response.json();
      })
      .then((task) => {

        if (!task || Object.keys(task).length === 0) {
          throw new Error("Пустой ответ от сервера");
        }

        // Описание задачи
        const taskInfo = document.querySelector("#task_info");
        if (taskInfo && task.description_main) {
          const title = document.createElement("h1");
          title.textContent = "Описание задачи";

          const ul = document.createElement("ul");

          task.description_main.forEach((item) => {
            const li = document.createElement("li");

            const subtitle = document.createElement("h3");
            subtitle.textContent = item.title;

            const description = document.createElement("p");
            description.textContent = item.value;

            li.appendChild(subtitle);
            li.appendChild(description);
            ul.appendChild(li);
          });

          taskInfo.appendChild(title);
          taskInfo.appendChild(ul);
        }

        // Ссылки
        const descriptionLinks = document.querySelector("#description_links");
        if (descriptionLinks && task.description_links) {
          const title = document.createElement("h2");
          title.textContent = "Ссылки";
          const ul = document.createElement("ul");

          task.description_links.forEach((link) => {
            const li = document.createElement("li");
            const linkIcon = document.createElement("img");
            linkIcon.src = "/static/task_info_page/images/link.svg";
            linkIcon.alt = "";
            linkIcon.className = "link-icon";
            const a = document.createElement("a");
            a.href = link.link;
            a.target = "_blank";
            a.textContent = link.name;
            li.appendChild(linkIcon);
            li.appendChild(a);
            ul.appendChild(li);
          });

          descriptionLinks.appendChild(title);
          descriptionLinks.appendChild(ul);
        }

        // Файлы
        const descriptionFiles = document.querySelector("#description_files");
        if (descriptionFiles && task.description_files) {
          const title = document.createElement("h2");
          title.textContent = "Файлы";
          const ul = document.createElement("ul");

          task.description_files.forEach((file) => {
            const size =
              file.file_size > 1024 * 1024
                ? `${(file.file_size / (1024 * 1024)).toFixed(2)} Мб`
                : `${(file.file_size / 1024).toFixed(2)} Кб`;
            const li = document.createElement("li");
            const fileIcon = document.createElement("img");
            fileIcon.src = "/static/task_info_page/images/file.svg";
            fileIcon.alt = "";
            fileIcon.className = "file-icon";
            const a = document.createElement("a");
            a.href = file.file_link;
            a.target = "_blank";
            a.textContent = `${file.file_name}`;
            const span = document.createElement("span");
            span.textContent = size;
            li.appendChild(fileIcon);
            li.appendChild(a);
            li.appendChild(span);
            ul.appendChild(li);
          });

          descriptionFiles.appendChild(title);
          descriptionFiles.appendChild(ul);
        }

        // Бонус от фонда
        const descriptionBonus = document.querySelector("#description_bonus");
        if (descriptionBonus && task.description_bonus) {
          const title = document.createElement("h2");
          title.textContent = "Бонус от фонда";
          const p = document.createElement("p");
          p.textContent = task.description_bonus;
          descriptionBonus.appendChild(title);
          descriptionBonus.appendChild(p);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        const p = document.createElement("p");
        p.textContent = error.message;
        destElement.appendChild(p);
      });
  }
}

view_query_parameters("main");
