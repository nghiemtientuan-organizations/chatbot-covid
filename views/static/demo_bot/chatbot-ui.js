/*
Makes backend API call to rasa chatbot and display output to chatbot frontend
*/

function init(botLogoPath) {

    //---------------------------- Including Jquery ------------------------------

    var script = document.createElement('script');
    script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js';
    script.type = 'text/javascript';
    document.getElementsByTagName('head')[0].appendChild(script);

    //--------------------------- Important Variables----------------------------
    // botLogoPath = "./imgs/bot-logo.png"

    //--------------------------- Chatbot Frontend -------------------------------
    const chatContainer = document.getElementById("chat-container");

    template = ` <button class='chat-btn' style="background-color: rgb(44, 93, 203); font-size: 24px; box-shadow: rgb(207 207 207 / 67%) 0px 2px 4px 0px;">
        <svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="comment-dots" class="svg-inline--fa fa-comment-dots fa-w-16 css-1fcbxrh" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" style="width: 1em;"><path fill="currentColor" d="M256 32C114.6 32 0 125.1 0 240c0 49.6 21.4 95 57 130.7C44.5 421.1 2.7 466 2.2 466.5c-2.2 2.3-2.8 5.7-1.5 8.7S4.8 480 8 480c66.3 0 116-31.8 140.6-51.4 32.7 12.3 69 19.4 107.4 19.4 141.4 0 256-93.1 256-208S397.4 32 256 32zM128 272c-17.7 0-32-14.3-32-32s14.3-32 32-32 32 14.3 32 32-14.3 32-32 32zm128 0c-17.7 0-32-14.3-32-32s14.3-32 32-32 32 14.3 32 32-14.3 32-32 32zm128 0c-17.7 0-32-14.3-32-32s14.3-32 32-32 32 14.3 32 32-14.3 32-32 32z"></path></svg>
    </button>

    <div class='chat-popup'>
    
		<div class='chat-header'>
			<div class='chatbot-img'>
				<img src='${botLogoPath}' alt='Chat Bot image' class='bot-img'> 
			</div>
			<h3 class='bot-title'>Covid Bot</h3>
			<button class = "expand-chat-window" ><img src="./icons/open_fullscreen.png" class="material-icon"></button>
		</div>

		<div class='chat-area'>
            <div class='bot-msg'>
                <img class='bot-img' src ='${botLogoPath}' />
				<span class='msg'>Hi, How can i help you?</span>
			</div>
			<div class="bot-msg bot-msg-selects">
			    <button class="customer-button-option">Bot có thể làm gì?</button>
			    <button class="customer-button-option">Hôm nay bao nhiêu độ?</button>
			    <button class="customer-button-option">Ăn gì được</button>
			    <button class="customer-button-option">Uống gì bây giờ</button>
			</div>
		</div>

		<div class='chat-input-area'>
			<input type='text' autofocus class='chat-input' onkeypress='return givenUserInput(event)' placeholder='Aa' autocomplete='off'>
			<button class='chat-submit'><i class='material-icons'>send</i></button>
		</div>
	</div>`

    chatContainer.innerHTML = template;
    // bot options first
    mapActionBotOption();

    //--------------------------- Important Variables----------------------------
    var inactiveMessage = "Server is down, Please contact the developer to activate it"


    chatPopup = document.querySelector(".chat-popup")
    chatBtn = document.querySelector(".chat-btn")
    chatSubmit = document.querySelector(".chat-submit")
    chatHeader = document.querySelector(".chat-header")
    chatArea = document.querySelector(".chat-area")
    chatInput = document.querySelector(".chat-input")
    expandWindow = document.querySelector(".expand-chat-window")
    root = document.documentElement;
    chatPopup.style.display = "none"
    var host = ""


    //------------------------ ChatBot Toggler -------------------------

    chatBtn.addEventListener("click", () => {

        mobileDevice = !detectMob()
        if (chatPopup.style.display == "none" && mobileDevice) {
            chatPopup.style.display = "flex"
            chatInput.focus();
            chatBtn.innerHTML = `<img src = "./icons/close.png" class = "material-icon" >`
        } else if (mobileDevice) {
            chatPopup.style.display = "none"
            chatBtn.innerHTML = `<svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="comment-dots" class="svg-inline--fa fa-comment-dots fa-w-16 css-1fcbxrh" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" style="width: 1em;"><path fill="currentColor" d="M256 32C114.6 32 0 125.1 0 240c0 49.6 21.4 95 57 130.7C44.5 421.1 2.7 466 2.2 466.5c-2.2 2.3-2.8 5.7-1.5 8.7S4.8 480 8 480c66.3 0 116-31.8 140.6-51.4 32.7 12.3 69 19.4 107.4 19.4 141.4 0 256-93.1 256-208S397.4 32 256 32zM128 272c-17.7 0-32-14.3-32-32s14.3-32 32-32 32 14.3 32 32-14.3 32-32 32zm128 0c-17.7 0-32-14.3-32-32s14.3-32 32-32 32 14.3 32 32-14.3 32-32 32zm128 0c-17.7 0-32-14.3-32-32s14.3-32 32-32 32 14.3 32 32-14.3 32-32 32z"></path></svg>`
        } else {
            mobileView()
        }
    })

    chatSubmit.addEventListener("click", () => {
        let userResponse = chatInput.value.trim();
        if (userResponse !== "") {
            setUserResponse();
            send(userResponse)
        }
    })

    expandWindow.addEventListener("click", (e) => {
        // console.log(expandWindow.innerHTML)
        if (expandWindow.innerHTML == '<img src="./icons/open_fullscreen.png" class="material-icon">') {
            expandWindow.innerHTML = `<img src = "./icons/close_fullscreen.png" class = 'material-icon'>`
            root.style.setProperty('--chat-window-height', 80 + "%");
            root.style.setProperty('--chat-window-total-width', 85 + "%");
            chatHeader.style.width = "100%";
        } else if (expandWindow.innerHTML == '<img src="./icons/close.png" class="material-icon">') {
            chatPopup.style.display = "none"
            chatBtn.style.display = "block"
        } else {
            expandWindow.innerHTML = `<img src = "./icons/open_fullscreen.png" class = "material-icon" >`
            root.style.setProperty('--chat-window-height', 500 + "px");
            root.style.setProperty('--chat-window-total-width', 380 + "px");
        }

    })
}


// to submit user input when he presses enter
function givenUserInput(e) {
    if (e.keyCode == 13) {
        let userResponse = chatInput.value.trim();
        if (userResponse !== "") {
            setUserResponse()
            send(userResponse)
        }
    }
}

// to display user message on UI
function setUserResponse(message = '') {
    const userInput = message || chatInput.value;
    const temp = `<div class="user-msg"><span class = "msg">${userInput}</span></div>`
    chatArea.innerHTML += temp;
    chatInput.value = ""
    mapActionBotOption();
    scrollToBottomOfResults();
}

function addBotOptions(options = []) {
    let optionElements = '<div class="bot-msg bot-msg-selects">';
    options.forEach(option => optionElements += `<button class="customer-button-option">${option}</button>`);
    optionElements += '</div>';
    chatArea.innerHTML += optionElements;

    mapActionBotOption();
}

function mapActionBotOption() {
    const customerOptions = document.getElementsByClassName('customer-button-option');
    Array.from(customerOptions).forEach(element => {
        element.addEventListener('click', () => {
            const customerOptionText = element.textContent.trim();
            if (customerOptionText !== "") {
                setUserResponse(customerOptionText);
                send(customerOptionText);
            }
        })
    });
}


function scrollToBottomOfResults() {
    chatArea.scrollTop = chatArea.scrollHeight;
}

/***************************************************************
Frontend Part Completed
****************************************************************/

// host = 'http://localhost:5005/webhooks/rest/webhook'
function send(message) {
    chatInput.focus();
    console.log("User Message:", message)
    $.ajax({
        url: host,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            "message": message,
            "sender": "User"
        }),
        success: function(data, textStatus) {
            if (data != null) {
                setBotResponse(data);
            }
            console.log("Rasa Response: ", data, "\n Status:", textStatus)
        },
        error: function(errorMessage) {
            setBotResponse("");
            console.log('Error' + errorMessage);

        }
    });
    chatInput.focus();
}


//------------------------------------ Set bot response -------------------------------------
function setBotResponse(val) {
    setTimeout(function() {
        if (val.length < 1) {
            //if there is no response from Rasa
            // msg = 'I couldn\'t get that. Let\' try something else!';
            msg = inactiveMessage;

            let BotResponse = `<div class='bot-msg'><img class='bot-img' src ='${botLogoPath}' /><span class='msg'> ${msg} </span></div>`;
            $(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
            scrollToBottomOfResults();
            chatInput.focus();

        } else {
            //if we get response from Rasa
            for (i = 0; i < val.length; i++) {
                //check if there is text message
                if (val[i].hasOwnProperty("text")) {
                    // insert text
                    const response = formatResponse(val[i].text);
                    const BotResponse = `<div class='bot-msg'><img class='bot-img' src='${botLogoPath}' /><span class='msg'>${response}</span></div>`;
                    $(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);

                    // insert options
                    if (response.indexOf('Tôi tìm được món này') > -1) {
                        setTimeout(() => {
                            addBotOptions([
                                'Nấu thế nào',
                                'Món khác',
                            ]);
                            scrollToBottomOfResults();
                        }, 1020);
                    }
                }

                //check if there is image
                if (val[i].hasOwnProperty("image")) {
                    console.log(val);
                    const BotResponse = "<div class='bot-msg'>" + `<img class='bot-img' src='${botLogoPath}' />` +
                    '<img class="msg-image" src="' + val[i].image + '">' +
                        '</div>'
                    $(BotResponse).appendTo('.chat-area').hide().fadeIn(1000);
                }
            }
            scrollToBottomOfResults();
            chatInput.focus();
        }

    }, 500);
}

function formatResponse(textResponse) {
    const urlRegex = /\[.{1,}\]\(.{1,}\)/g;

    return textResponse.replace(/\r?\n/g, "<br />")
        .replace(urlRegex, function (url) {
            const text = url.replace('[', '')
                .replace(/\]\(.{1,}\)/, '');
            const link = url.replace(')', '')
                .replace(/\[.{1,}\]\(/, '');

            return `<a href="${link}" class="food-link" target="_blank">${text}</a>`;
        });
}

function mobileView() {
    $('.chat-popup').width($(window).width());

    if (chatPopup.style.display == "none") {
        chatPopup.style.display = "flex"
            // chatInput.focus();
        chatBtn.style.display = "none"
        chatPopup.style.bottom = "0"
        chatPopup.style.right = "0"
            // chatPopup.style.transition = "none"
        expandWindow.innerHTML = `<img src = "./icons/close.png" class = "material-icon" >`
    }
}

function detectMob() {
    return ((window.innerHeight <= 800) && (window.innerWidth <= 600));
}

function chatbotTheme(theme) {
    const gradientHeader = document.querySelector(".chat-header");
    const orange = {
        color: "#FBAB7E",
        background: "linear-gradient(19deg, #FBAB7E 0%, #F7CE68 100%)"
    }

    const purple = {
        color: "#B721FF",
        background: "linear-gradient(19deg, #21D4FD 0%, #B721FF 100%)"
    }



    if (theme === "orange") {
        root.style.setProperty('--chat-window-color-theme', orange.color);
        gradientHeader.style.backgroundImage = orange.background;
        chatSubmit.style.backgroundColor = orange.color;
    } else if (theme === "purple") {
        root.style.setProperty('--chat-window-color-theme', purple.color);
        gradientHeader.style.backgroundImage = purple.background;
        chatSubmit.style.backgroundColor = purple.color;
    }
}

function createChatBot(hostURL, botLogo, title, welcomeMessage, inactiveMsg, theme = "blue") {

    host = hostURL;
    botLogoPath = botLogo;
    inactiveMessage = inactiveMsg;
    init(botLogoPath)
    const msg = document.querySelector(".msg");
    msg.innerText = welcomeMessage;

    const botTitle = document.querySelector(".bot-title");
    botTitle.innerText = title;

    chatbotTheme(theme)
}