document.addEventListener("DOMContentLoaded", function () {

    const progressBars = document.querySelectorAll(
        ".progress-fill"
    );

    progressBars.forEach(function (bar) {

        const progress = parseFloat(
            bar.dataset.progress
        ) || 0;

        bar.style.width = progress + "%";

    });

});

