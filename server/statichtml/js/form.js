function showModal(status) {
  if (status == null) {
    //
  } else {
    document.getElementById("status_box").innerHTML = status;
    document.getElementById("status-button").click();
  }
}

let listOfSelectedFiles = []
const hostName = window.location.origin;
let noOfFilesSent = 0;
let responsesList = []

function clearFiles() {
  listOfSelectedFiles = [];
  inputFilesElement = document.getElementById("uploadFile");
  inputFilesElement.value = "";
  console.log(inputFilesElement.files);
  listSelectedFiles();
}

function clearMessageInput() {
  let messageForm = document.forms["messageForm"];
  let message = messageForm["message"];
  message.value = ""
}

function listSelectedFiles() {
  listElement = document.getElementById("uploadFileList");
  inputFilesElement = document.getElementById("uploadFile");
  listOfSelectedFiles = []

  while (listElement.lastElementChild) {
    listElement.removeChild(listElement.lastElementChild);
  };
  
  const fileList = inputFilesElement.files
  const fileSizeLimit = 50;

  if (fileList.length === 0) {
    ;
  } else {
    for (const file of fileList) {

      fileSize = (file.size/1024/1024).toPrecision(2);

      if (fileSize > fileSizeLimit) {
        showModal(`Please select files below ${fileSizeLimit}MB.`);
        continue;
      }
      const listItem = document.createElement("li");
      listItem.setAttribute("class","col-6 mb-2");
      listItem.textContent = `${file.name}  | ${fileSize} MB`;

      const progressBar = document.createElement("div");
      const progressBarDiv = document.createElement("div");
      progressBarDiv.setAttribute("class", "progress col-6 p-0");
      progressBar.setAttribute("class","progress-bar w-0");
      progressBar.setAttribute("role", "progressbar");
      progressBar.setAttribute("aria-valuenow", "0");
      progressBar.setAttribute("aria-valuemin", "0");
      progressBar.setAttribute("aria-valuemax", "100");
      progressBarDiv.appendChild(progressBar);

      listOfSelectedFiles.push({
        file,
        progressBar
      })
      listElement.appendChild(listItem);
      listElement.appendChild(progressBarDiv);
    }

    warningText = document.createElement("p");
    warningText.setAttribute("class","text-danger");
    warningText.textContent = "Note that it will take sometime to forward your file after upload progress is 100%. So please don't close this tab until you get status."
    removeButton = document.createElement("button");
    removeButton.setAttribute("class","btn btn-secondary col-4 col-md-2 mt-3 mb-3 offset-4 offset-md-5");
    removeButton.textContent = "clear";
    removeButton.addEventListener("click",clearFiles);

    listElement.appendChild(removeButton);
    listElement.appendChild(warningText);
  }
}

function makeRequest(currentFileObject, formData) {
  const xhr = new XMLHttpRequest();

  xhr.upload.addEventListener("progress", (event) => {

    if (event.lengthComputable) {
      const uploadProgress = Math.floor(event.loaded / event.total) * 100;
      currentFileObject.progressBar.style.width = `${uploadProgress}%`;
    }
  });

  xhr.onreadystatechange = () => {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      noOfFilesSent++;
      response = xhr.responseText;
      response = JSON.parse(response);
      if (response.hasOwnProperty("error")) {
        responsesList.push(`Error in file ${currentFileObject.file.name}: ` + response["error"]);
      }
      else if (response["status"] != "success") {
        responsesList.push(`Error in file ${currentFileObject.file.name}: Unknown Error.`);
      }
      else {
        responsesList.push(`File ${currentFileObject.file.name}: SUCCESS`);
      }
    }

    if (noOfFilesSent === listOfSelectedFiles.length) {
      showFinalOutput(responsesList);
    }
  };

  xhr.open("POST", hostName + "/api/sendfile");
  xhr.send(formData);
}

async function sendMessage() {
  let messageForm = document.forms["messageForm"];
  let username = messageForm["telegramUsername"].value;
  let message = messageForm["message"].value;
  let key = parseInt(messageForm["securityKey"].value);
  noOfFilesSent = 0; // Unset noOfFilesSent
  responsesList = [];

  if (message === "" && listOfSelectedFiles.length === 0) {
    showModal("Please enter a message or select a file");
    return;
  }

  document.getElementById("submit-button").disabled = true;
  setTimeout(
    () => (document.getElementById("submit-button").disabled = false),
    4000
  );

  if (isNaN(key)) {
    alert("Please enter a number in security key field.");
    return 0;
  }

  if (message !== "") {
    let messageReqJson = {
      username: username,
      message: message,
      securitykey: key,
    };

    let query = await fetch(hostName + "/api/sendmessage", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(messageReqJson),
    });

    let respJson = await query.json();
    if (respJson.hasOwnProperty("error")) {
      responsesList.push("Error in text: " + respJson["error"]);
    }
    else if (respJson["status"] != "success") {
      responsesList.push("Error in text: UNKNOWN ERROR");
    }
    else {
      responsesList.push("Message: SUCCESS");
    }

    if (listOfSelectedFiles.length === 0) {
      showFinalOutput(responsesList);
    }
  }

  if (listOfSelectedFiles !== 0) {
    
    for (fileObject of listOfSelectedFiles) {
      
      let formData = new FormData();
      formData.append("file", fileObject.file);
      formData.append("username", username);
      formData.append("securitykey", key);
      fileObject.progressBar.style.width = "0%";

      makeRequest(fileObject, formData);
    }
  }
}

function showFinalOutput(outList) {
  let finalOutput = "";
  for (responseText of outList) {
    finalOutput += responseText + "<br>";
  }
  showModal(finalOutput);
  clearFiles();
  clearMessageInput();
  noOfFilesSent = 0; // Unset noOfFilesSent
  responsesList = [];
}

listElement = document.getElementById("uploadFile");
listElement.addEventListener("change",listSelectedFiles);
listSelectedFiles();
