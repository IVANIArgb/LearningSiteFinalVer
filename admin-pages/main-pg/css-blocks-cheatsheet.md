# Шпаргалка по стилям блоков проекта

## Основные блоки и их стили

### .main-page-user-type
- **display: flex; flex-direction: row; justify-content: center;** — основной контейнер, выравнивает содержимое по центру.
- **background-color: #fff; width: 100%;** — белый фон, ширина на всю страницу.

### .main-page-user-type .div
- **background-color: #fff; overflow: hidden; width: 1920px; height: 1358px; position: relative;** — основной внутренний контейнер, фиксированные размеры, скрывает переполнение.

### .main-page-user-type .view
- **position: absolute; width: 1920px; height: 346px; top: 974px; left: 0; border-radius: 12px; overflow: hidden; background: linear-gradient(...);** — секция с градиентом, абсолютное позиционирование.

### .main-page-user-type .image
- **position: absolute; width: 1920px; height: 100px; top: 246px; left: 0; object-fit: cover;** — изображение, растягивается на всю ширину блока.

### .main-page-user-type .text-wrapper, .text-wrapper-*
- **position: absolute;** — текстовые элементы с индивидуальным позиционированием.
- **font-family, font-size, color** — индивидуальные настройки шрифта и цвета.

### .main-page-user-type .letters-group-wrapper, .letters-group, .overlap-group
- **position: absolute/relative; width/height; background-color; border-radius;** — оформление логотипа, группировка SVG-букв.

### .main-page-user-type .header
- **position: absolute; width: 1920px; height: 110px; top: 0; left: 1px; background-color: #6293ae; border-radius: 12px; overflow: hidden;** — шапка сайта.

### .main-page-user-type .info-box
- **position: absolute; width: 286px; height: 56px; top: 27px; left: 1356px;** — блок с ФИО пользователя.

### .main-page-user-type .slide
- **position: absolute; width: 1921px; height: 864px; top: 110px; left: 0; background-color: #fff; border-radius: 12px; overflow: hidden;** — основной контентный блок.

### .main-page-user-type .group
- **position: relative; width: 1360px; height: 620px; top: 73px; left: 281px;** — внутренний контейнер для контента.

### .main-page-user-type .logo-group
- **position: absolute; width: 279px; height: 80px; top: 15px; left: 275px;** — блок с логотипом.

### .main-page-user-type .labels, .site-name
- **position: absolute; width: 183px; height: 67px; top: 7px; left: 100px;** — подписи и название сайта.

### .main-page-user-type .component
- **position: absolute; width: 51px; height: 30px; top: 32px; left: 894px;** — иконка/картинка.

### .main-page-user-type .view-2 ... .view-14
- **position: absolute; width/height; top/left;** — различные секции и подблоки, часто используются для меню, карточек, новостей и т.д.

### .main-page-user-type .rectangle-*, .overlap-*, .side-labels, .rows, .row-content
- **position: absolute/relative; width/height; background-color; border; border-radius;** — декоративные и структурные элементы, прямоугольники, разделители, контейнеры для строк и колонок.

---

## Адаптивные стили (медиазапросы)

- **@media (max-width: 1200px), (900px), (600px)** — изменяют размеры, расположение, шрифты и отступы для корректного отображения на разных устройствах.
- Пример: `.main-page-user-type .div { width: 100vw; }` — на мобильных и планшетах ширина блока становится 100% ширины экрана.

---

## Цветовые переменные (из styleguide.css)

- Используются CSS-переменные, например: `--itproger-com-color-red-63: rgba(242, 102, 81, 1);`
- Применяются для фонов, текста, градиентов, бордеров.

---

## Пример структуры блока

```html
<div class="main-page-user-type">
  <div class="div">
    <div class="view">
      <img class="image" src="img/image.svg" />
      <div class="text-wrapper">LearnSite</div>
      ...
    </div>
    ...
  </div>
</div>
```

---

Если нужно расшифровать конкретный класс или свойство — напишите его название, и я объясню, что оно делает! 