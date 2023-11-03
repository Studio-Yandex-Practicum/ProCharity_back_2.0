// validation settings and check actions
const validationConfig = {
  name: {
    isCapitalize: true,
  },
  surname: {
    isCapitalize: true,
  },
  email: {
    isCapitalize: false,
  },
  feedback: {
    isCapitalize: false,
  },
};

const errMsg = {
  name: {
    required: 'Пожалуйста, укажите имя',
    min: 'Введите не менее 2 символов',
    max: 'Допускается ввод не более 100 символов',
    capsPattern: 'Убедитесь, что y Bac выключен CAPS LOCK',
    dashPattern: 'Убедитесь, что дефис находится в нужном месте',
    nameSurnamePattern: 'Доступно использование только кириллицы, латиницы и "-"',
  },
  surname: {
    required: 'Пожалуйста, укажите фамилию',
    min: 'Введите не менее 2 символов',
    max: 'Допускается ввод не более 100 символов',
    capsPattern: 'Убедитесь, что y Bac выключен CAPS LOCK',
    dashPattern: 'Убедитесь, что дефис находится в нужном месте',
    nameSurnamePattern: 'Доступно использование только кириллицы, латиницы и "-"',
  },
  email: {
    required: 'Пожалуйста, укажите ваш email',
    capsPattern: 'Убедитесь, что y Bac выключен CAPS LOCK',
    emailPattern:
      'Неверный формат адреса email. Используйте только латиницу, "-", "@" и "_"',
  },
  feedback: {
    required: 'Пожалуйста, напишите ваш отзыв',
    min: 'Введите не менее 10 символов',
    max: 'Допускается ввод не более 500 символов',
    capsPattern: 'Убедитесь, что y Bac выключен CAPS LOCK',
    feedbackPattern:
      'Доступно использование только кириллицы, латиницы и символов: "-", "_", ".", "," и "!"',
  },
};

const disabledTgButtonColor = '#9e9e9e';
const disabledTgButtonTextColor = '#eceff1';

const setValid = (element, errElement) => {
  element.classList.remove('invalid');
  errElement.textContent = '';
};

const setInvalid = (element, errElement, errName) => {
  element.classList.add('invalid');
  errElement.textContent = errMsg[element.name][errName];
};

const checkInputValidity = (element, errElement, pattern, isCapitalize) => {
  let newValue = element.value;
  const minlength = element.getAttribute('minlength');
  const maxlength = element.getAttribute('maxlength');
  const capsPattern = /[А-ЯЁ]{2,}/g;
  const dashPattern = /( -)|(- )|(^-)|(-$)/g;
  const phonePattern = /^\+7 [3489]\d{2} \d{3}-\d{2}-\d{2}$/;
  const nameSurnamePattern = /^[А-ЯЁA-Z][а-яёa-z]*([-][А-ЯЁA-Z][а-яёa-z]+)*$/g;
  const emailPattern = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/g;
  const feedbackPattern = /[А-ЯЁа-яёa-zA-Z0-9._!@/-]/g;

  if (pattern) {
    newValue = newValue.trimStart().replace(pattern, '');
  }

  // convert phone number to international format: +7 DEF XXX-XX-XX
  if (newValue && element.name === 'phone_number') {
    newValue = newValue
      .replace(/^(?:7|8)?(\d{0,3})?(\d{0,3})(\d{0,2})(\d*)$/, '+7 $1 $2-$3-$4')
      .replace(/\D(?!\d)/g, ''); // remove trailing hyphens (non-digit not followed by a digit)
  }

  if (isCapitalize && newValue) {
    newValue = newValue
      .split('-')
      .map((word) =>
        word
          ? word.replace(
              /^(?!на)[а-яё]{2}/,
              (letter) => letter[0].toUpperCase() + letter.slice(1)
            )
          : ''
      )
      .join('-')
      .split(' ')
      .map((word) => (word ? word[0].toUpperCase() + word.slice(1) : ''))
      .join(' ');
  }

  if (!newValue) {
    setInvalid(element, errElement, 'required');
  } else if (minlength && newValue.length < minlength) {
    setInvalid(element, errElement, 'min');
  } else if (maxlength && newValue.length > maxlength) {
    setInvalid(element, errElement, 'max');
  } else if (newValue.match(capsPattern)) {
    setInvalid(element, errElement, 'capsPattern');
  } else if (newValue.match(dashPattern)) {
    setInvalid(element, errElement, 'dashPattern');
  } else if (element.name === 'phone_number' && !newValue.match(phonePattern)) {
    setInvalid(element, errElement, 'phonePattern');
  } else if (
    (element.name === 'name' || element.name === 'surname') &&
    !newValue.match(nameSurnamePattern)
  ) {
    setInvalid(element, errElement, 'nameSurnamePattern');
  } else if (element.name === 'email' && !newValue.match(emailPattern)) {
    setInvalid(element, errElement, 'emailPattern');
  } else if (element.name === 'feedback' && !newValue.match(feedbackPattern)) {
    setInvalid(element, errElement, 'feedbackPattern');
  } else {
    setValid(element, errElement);
  }

  element.value = newValue;
};

const toggleSubmitState = (
  inputs,
  tgMainButton,
  defaultButtonColor,
  defaultButtonTextColor
) => {
  const isValidationError = Array.from(inputs).some(
    (input) => !input.validity.valid || input.classList.contains('invalid')
  );

  if (isValidationError) {
    tgMainButton.setParams({
      is_active: false,
      color: disabledTgButtonColor,
      text_color: disabledTgButtonTextColor,
    });
  } else {
    tgMainButton.setParams({
      is_active: true,
      color: defaultButtonColor,
      text_color: defaultButtonTextColor,
    });
  }
};

const setValidation = (
  inputs,
  tgMainButton,
  defaultButtonColor,
  defaultButtonTextColor
) => {
  toggleSubmitState(
    inputs,
    tgMainButton,
    defaultButtonColor,
    defaultButtonTextColor
  );

  inputs.forEach((input) => {
    const { pattern, isCapitalize } = validationConfig[input.name];

    const errElement = document.querySelector(`.helper-text.${input.name}`);

    const check = () => {
      checkInputValidity(input, errElement, pattern, isCapitalize);
      toggleSubmitState(
        inputs,
        tgMainButton,
        defaultButtonColor,
        defaultButtonTextColor
      );
    };

    input.oninput = () => check();
    input.onblur = () => check();
    input.onchange = () => check();
    input.onpaste = () => check();
  });
};

const params = new Proxy(new URLSearchParams(window.location.search), {
  get: (searchParams, prop) => searchParams.get(prop),
});

if (params.surname) {
  document.getElementById('name').value = params.name;
  document.getElementById('surname').value = params.surname;
  document.getElementById('email').value = params.email;
  document.getElementById('feedback').value = params.feedback;
}

if (params.update) {
  var formText = `Рады снова видеть Вас в нашем проекте.<br>
        Пожалуйста, проверьте свои данные.`;
  var buttonText = 'Подать заявку на участие в смене';
} else {
  var formText = '* необходимо заполнить поля';
  var buttonText = 'Зарегистрироваться в проекте';
}

document.getElementById('formtitle').innerHTML = formText;

const showTgButton = (tgMainButton) => {
  tgMainButton.setText(buttonText);
  tgMainButton.show();
};

// send data to server
const handleSubmit = (inputs, tg) => {
  tg.MainButton.disable();

  const data = Array.from(inputs).reduce((data, input) => {
    data[input.name] = input.value.trim();
    return data;
  }, {});

  tg.sendData(JSON.stringify(data));
  tg.close();
};

// content loaded, main actions
document.addEventListener('DOMContentLoaded', function () {
  const tg = window.Telegram.WebApp;
  tg.ready();
  tg.expand();

  const tgMainButton = tg.MainButton;
  const defaultButtonColor = tg.themeParams.button_color;
  const defaultButtonTextColor = tg.themeParams.button_text_color;

  const inputElements = document.querySelectorAll('.validate');

  setValidation(
    inputElements,
    tgMainButton,
    defaultButtonColor,
    defaultButtonTextColor
  );

  tgMainButton.onClick(() => handleSubmit(inputElements, tg));
  showTgButton(tgMainButton);
});

document.addEventListener('DOMContentLoaded', function () {
  const checkbox = document.querySelector('#checkbox');
  const emailSection = document.querySelector('#email_section');
  const email = document.querySelector('#email');
  checkbox.addEventListener('change', function (element) {
    if (checkbox.checked) {
      emailSection.style.display = 'block';
    } else {
      email.value = '';
      const emailErr = document.querySelector('.helper-text.email');
      setValid(email, emailErr);
      email.classList.remove('valid');
      emailSection.style.display = 'none';
    }
  });
});
