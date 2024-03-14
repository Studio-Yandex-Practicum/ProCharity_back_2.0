// Validation Functions
const required = (v) => {return new Boolean(v)}
const needToBePattern = (pattern) => {return (v) => {return v.match(pattern)}}
const dontNeedToBePattern = (pattern) => {return (v) => {return !v.match(pattern)}}
const hasMinLength = (minlength) => {return (v) => {return v.length > minlength}}
const hasMaxLength = (maxlength) => {return (v) => {return v.length < maxlength}}

// Patterns
const capsPattern = /[А-ЯЁ]{2,}/g;
const dashPattern = /( -)|(- )|(^-)|(-$)/g;
const nameSurnamePattern = /^[A-Za-zА-Яа-я]*([-][A-Za-zА-Яа-я]+)*$/g;
const emailPattern = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/g;

// validation settings and check actions
const validationConfig = {
  name: [
    {func: required, errMsg: 'Пожалуйста, укажите имя'},
    {func: needToBePattern(nameSurnamePattern), errMsg: 'Доступно использование только кириллицы, латиницы и "-"'},
    {func: dontNeedToBePattern(dashPattern), errMsg: 'Убедитесь, что дефис находится в нужном месте'},
    {func: dontNeedToBePattern(capsPattern), errMsg: 'Убедитесь, что y Bac выключен CAPS LOCK'},
    {func: hasMinLength(1), errMsg: 'Введите не менее 2 символов'},
    {func: hasMaxLength(100), errMsg: 'Допускается ввод не более 100 символов'},
  ],
  surname: [
    {func: needToBePattern(nameSurnamePattern), errMsg: 'Доступно использование только кириллицы, латиницы и "-"'},
    {func: dontNeedToBePattern(dashPattern), errMsg: 'Убедитесь, что дефис находится в нужном месте'},
    {func: dontNeedToBePattern(capsPattern), errMsg: 'Убедитесь, что y Bac выключен CAPS LOCK'},
    {func: hasMinLength(1), errMsg: 'Введите не менее 2 символов'},
    {func: hasMaxLength(100), errMsg: 'Допускается ввод не более 100 символов'},
  ],
  email: [
    {func: needToBePattern(emailPattern), errMsg: 'Неверный формат адреса email. Используйте только латиницу, "-", "@" и "_"'},
    {func: hasMaxLength(100), errMsg: 'Допускается ввод не более 100 символов'},
  ],
  message: [
    {func: hasMinLength(1), errMsg: 'Введите не менее 2 символов'},
    {func: hasMaxLength(2500), errMsg: 'Допускается ввод не более 2500 символов'},
  ],
  telegram_link: [],
  external_id: [],
};

const disabledTgButtonColor = '#9e9e9e';
const disabledTgButtonTextColor = '#eceff1';

const setValid = (element, errElement) => {
  element.classList.remove('invalid');
  errElement.textContent = '';
};

const setInvalid = (element, errElement, errMsg) => {
  element.classList.add('invalid');
  errElement.textContent = errMsg;
};

const checkInputValidity = (element, errElement, validators) => {
  let value = element.value;
  let errors = new Array(validators.length)
  let isValid = true

  for (const property in validators) {
    const{ func, errMsg } = validators[property]
    if (func(value)) {
      continue
    }
    isValid = false;
    errors.push(errMsg);
  }
  if (isValid) {
    setValid(element, errElement)
  } else {
    setInvalid(element, errElement, errors.join("\n"))
  }
};

const activateButton = (tgMainButton) => {
  tgMainButton.setParams({
    is_active: true,
    color: defaultButtonColor,
    text_color: defaultButtonTextColor,
  });

}

const deactivateButton = (tgMainButton) => {
  tgMainButton.setParams({
    is_active: false,
    color: disabledTgButtonColor,
    text_color: disabledTgButtonTextColor,
  });
}

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
    return deactivateButton(tgMainButton)
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
    const validators = validationConfig[input.name];
    const errElement = document.querySelector(`.helper-text.${input.name}`);
    const check = () => {
      checkInputValidity(input, errElement, validators);
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

if (params.name) {
  document.getElementById('name').value = params.name;
};
if (params.surname) {
  document.getElementById('surname').value = params.surname;
};
if (params.email) {
  document.getElementById('email').value = params.email;
};
if (params.telegram_link) {
  document.getElementById('telegram_link').value = params.telegram_link;
};
if (params.external_id) {
  document.getElementById('external_id').value = params.external_id;
};

if (params.update) {
  var formText = `Рады снова видеть Вас в нашем проекте.<br>
        Пожалуйста, проверьте свои данные.`;
  var buttonText = 'Подать заявку на участие в смене';
} else {
  var formText = '* необходимо заполнить поля';
  var buttonText = 'Отправить';
}

document.getElementById('formtitle').innerHTML = formText;

const showTgButton = (tgMainButton) => {
  tgMainButton.setText(buttonText);
  tgMainButton.show();
};

// send data to server
const handleSubmit = async (inputs, tg) => {
  tg.MainButton.disable();

  const data = Array.from(inputs).reduce((data, input) => {
    data[input.name] = input.value.trim();
    return data;
  }, {});

  var header = new Headers([["Content-Type", "application/json"]]);

  return await fetch("/api/feedback", { method: "POST", body: JSON.stringify(data), headers: header }).then((res) => {
    if (res.ok) {
      return tg.close()
    }
    res.json().then((data) => {
      if (data == null) {
        return alert(`Server response with status ${res.status()}!`)
      }
      return alert(data)
    })
  })
};

function validate () {
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

  tgMainButton.onClick(async () => await handleSubmit(inputElements, tg));
  showTgButton(tgMainButton);
}

// content loaded, main actions
document.addEventListener('DOMContentLoaded', validate);
validate();

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
