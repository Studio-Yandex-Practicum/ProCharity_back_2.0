dayjs.extend(dayjs_plugin_customParseFormat);

    // datepicker options
    const i18nOptions = {
      cancel: "Отменить",
      done: "Ок",
      months: [
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
      ],
      monthsShort: [
        "Янв",
        "Фев",
        "Мар",
        "Апр",
        "Май",
        "Июн",
        "Июл",
        "Авг",
        "Сен",
        "Окт",
        "Ноя",
        "Дек",
      ],
      weekdays: [
        "Воскресенье",
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
      ],
      weekdaysShort: ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"],
      weekdaysAbbrev: ["Вc", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"],
    };

    // validation settings and check actions
    const validationConfig = {
      name: {
        pattern: /[^ЁА-Яёа-я-]/g,
        isCapitalize: true,
      },
      surname: {
        pattern: /[^ЁА-Яёа-я-]/g,
        isCapitalize: true,
      },
      date_of_birth: {
        pattern: /[^\d.]/g,
        isCapitalize: false,
      },
      city: {
        pattern: /[^ЁА-Яёа-я- ]/g,
        isCapitalize: true,
      },
      phone_number: {
        pattern: /[^\d]/g,
        isCapitalize: false,
      },
    };

    const errMsg = {
      name: {
        required: "Пожалуйста, укажите имя",
        min: "Введите не менее 2 символов",
        max: "Допускается ввод не более 100 символов",
        capsPattern: "Убедитесь, что у Вас выключен CAPS LOCK",
        dashPattern: "Убедитесь, что дефис находится в нужном месте",
        nameSurnamePattern: "Доступно использование только кириллицы и \"-\"",
      },
      surname: {
        required: "Пожалуйста, укажите фамилию",
        min: "Введите не менее 2 символов",
        max: "Допускается ввод не более 100 символов",
        capsPattern: "Убедитесь, что у Вас выключен CAPS LOCK",
        dashPattern: "Убедитесь, что дефис находится в нужном месте",
        nameSurnamePattern: "Доступно использование только кириллицы и \"-\"",
      },
      date_of_birth: {
        required: "Пожалуйста, укажите дату рождения",
        invalidDate: "Введите дату в формате дд.мм.гггг",
      },
      city: {
        required: "Пожалуйста, укажите название города",
        min: "Введите не менее 2 символов",
        max: "Допускается ввод не более 50 символов",
        capsPattern: "Убедитесь, что у Вас выключен CAPS LOCK",
        dashPattern: "Убедитесь, что дефис находится в нужном месте",
        cityPattern: "Доступно использование только кириллицы, пробела и \"-\"",
      },
      phone_number: {
        required: "Пожалуйста, укажите номер телефона",
        min: "Введите номер телефона",
        max: "Номер телефона не должен содержать более 11 цифр",
        phonePattern: `Допускаются номера только мобильных
          операторов РФ: \"+7\u00A03.........\" или \"+7\u00A04.........\" или \"+7\u00A09.........\"`,
      },
    };

    const dateFormatDayjs = "DD.MM.YYYY";
    const disabledTgButtonColor = "#9e9e9e";
    const disabledTgButtonTextColor = "#eceff1";

    const setValid = (element, errElement) => {
      element.classList.remove("invalid");
      errElement.textContent = "";
    };

    const setInvalid = (element, errElement, errName) => {
      element.classList.add("invalid");
      errElement.textContent = errMsg[element.name][errName];
    };

    const checkInputValidity = (
      element,
      errElement,
      pattern,
      isCapitalize
    ) => {
      let newValue = element.value;
      const minlength = element.getAttribute("minlength");
      const maximumlength = element.getAttribute("maximumlength");
      const capsPattern = /[А-ЯЁ]{2,}/g;
      const dashPattern = /( -)|(- )|(^-)|(-$)/g;
      const phonePattern = /^\+7 [3489]\d{2} \d{3}-\d{2}-\d{2}$/;
      const nameSurnamePattern = /^[А-ЯЁ][а-яё]*([-][А-ЯЁ][а-яё]+)*$/g;
      const cityPattern = /^[А-ЯЁ][а-яё]*(([-][А-ЯЁ][а-яё]+)|[-](на)+)*([\s][А-ЯЁ][а-яё]+)*$/g;

      if (pattern) {
        newValue = newValue.trimStart().replace(pattern, "");
      }

      // convert phone number to international format: +7 DEF XXX-XX-XX
      if (newValue && element.name === "phone_number") {
        newValue = newValue
          .replace(/^(?:7|8)?(\d{0,3})?(\d{0,3})(\d{0,2})(\d*)$/, "+7 $1 $2-$3-$4")
          .replace(/\D(?!\d)/g, ""); // remove trailing hyphens (non-digit not followed by a digit)
      }

      if (isCapitalize && newValue) {
        newValue = newValue
          .split("-")
          .map((word) => (
            word ? word.replace(
              /^(?!на)[а-яё]{2}/, letter => letter[0].toUpperCase() + letter.slice(1)
            ) : "")
          )
          .join("-")
          .split(" ")
          .map((word) => (word ? word[0].toUpperCase() + word.slice(1) : ""))
          .join(" ");
      }

      if (!newValue) {
        setInvalid(element, errElement, "required");
      } else if (
        element.name === "date_of_birth" &&
        !dayjs(newValue, dateFormatDayjs, true).isValid()
      ) {
        setInvalid(element, errElement, "invalidDate");
      } else if (minlength && newValue.length < minlength) {
        setInvalid(element, errElement, "min");
      } else if (maximumlength && newValue.length > maximumlength) {
        setInvalid(element, errElement, "max");
      } else if (newValue.match(capsPattern)) {
        setInvalid(element, errElement, "capsPattern");
      } else if (newValue.match(dashPattern)) {
        setInvalid(element, errElement, "dashPattern");
      } else if (
        element.name === "phone_number" && !(newValue.match(phonePattern))
      ) {
        setInvalid(element, errElement, "phonePattern");
      } else if (
        (element.name === "name" || element.name === "surname") &&
        !(newValue.match(nameSurnamePattern))
      ) {
        setInvalid(element, errElement, "nameSurnamePattern");
      } else if (
        element.name === "city" && !(newValue.match(cityPattern))
      ) {
        setInvalid(element, errElement, "cityPattern");
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
        (input) =>
          !input.validity.valid || input.classList.contains("invalid")
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

        const errElement = document.querySelector(
          `.helper-text.${input.name}`
        );

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
      document.getElementById("name").value = params.name;
      document.getElementById("surname").value = params.surname;
      document.getElementById("date_of_birth").value = params.date_of_birth;
      document.getElementById("city").value = params.city;
      document.getElementById("phone_number").value = params.phone_number;
    }

    if (params.update) {
      var formText = `Рады снова видеть Вас в нашем проекте.<br>
        Пожалуйста, проверьте свои данные.`;
      var buttonText = "Подать заявку на участие в смене";
    } else {
      var formText = "Пожалуйста, заполните данную форму.";
      var buttonText = "Зарегистрироваться в проекте";
    }

    document.getElementById("formtitle").innerHTML = formText

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
    document.addEventListener("DOMContentLoaded", function () {
      const tg = window.Telegram.WebApp;
      tg.ready();
      tg.expand();

      const tgMainButton = tg.MainButton;
      const defaultButtonColor = tg.themeParams.button_color;
      const defaultButtonTextColor = tg.themeParams.button_text_color;

      const inputElements = document.querySelectorAll(".validate");
      const datePickerElement = document.querySelector(".datepicker");

      const today = new Date();
      const currentYear = today.getFullYear();

      const datePickerInstance = M.Datepicker.init(datePickerElement, {
        format: "dd.mm.yyyy",
        maxDate: today,
        yearRange: [1945, currentYear],
        firstDay: 1,
        i18n: { ...i18nOptions },
        onDraw() {
          const selects = document.querySelectorAll(".datepicker-select");
          selects.forEach((select) => {
            select.classList.add("browser-default");
          });

          const selectInputs = document.querySelectorAll(".select-dropdown");
          selectInputs.forEach((input) => {
            input.remove();
          });
        },
      });

      setValidation(
        inputElements,
        tgMainButton,
        defaultButtonColor,
        defaultButtonTextColor
      );

      tgMainButton.onClick(() => handleSubmit(inputElements, tg));
      showTgButton(tgMainButton);
    });
