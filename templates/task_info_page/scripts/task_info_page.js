function view_query_parameters(destElementSelector) {
    let destElement = document.querySelector(destElementSelector);
    if (destElement) {
        const searchParams = new URL(document.location).searchParams;
        for (const [key, value] of searchParams) {
            let paramElement = document.createElement('p');
            paramElement.innerText = `${key} = ${value}`;
            destElement.append(paramElement);
        }
    }
}

view_query_parameters('main');
