import {
  Canvg,
  presets
} from 'https://cdn.skypack.dev/canvg@^4.0.1';

const langMappings = {
  'de': {
    marginLeft: 205.0,
    yLabel: 'note',
    xLabel: 'leute',
    labels: [
      { grade: 8.0, text: ' N fail' },
      { grade: 7.0, text: ' B pass' },
      { grade: 6.0, text: ' × Nicht erschienen - nicht ausreichend' },
      { grade: 4.1, text: ' nicht ausreichend' },
      { grade: 3.4, text: ' ausreichend' },
      { grade: 2.4, text: ' befriedigend' },
      { grade: 1.4, text: ' gut' },
      { grade: 0.0, text: ' sehr gut' },
    ]
  },
  'en': {
    marginLeft: 175.0,
    yLabel: 'grade',
    xLabel: 'people',
    labels: [
      { grade: 8.0, text: ' N fail' },
      { grade: 7.0, text: ' B pass' },
      { grade: 6.0, text: ' × Didn\'t show up - not sufficient' },
      { grade: 4.1, text: ' not sufficient' },
      { grade: 3.4, text: ' sufficient' },
      { grade: 2.4, text: ' satisfactory' },
      { grade: 1.4, text: ' good' },
      { grade: 0.0, text: ' very good' },
    ]
  },
  'none': {
    marginLeft: 35.0,
    yLabel: 'grade',
    xLabel: 'people',
    labels: [
      { grade: 8.0, text: '' },
      { grade: 7.0, text: '' },
      { grade: 6.0, text: ' ×' },
      { grade: 4.1, text: '' },
      { grade: 3.4, text: '' },
      { grade: 2.4, text: '' },
      { grade: 1.4, text: '' },
      { grade: 0.0, text: '' },
    ]
  },
};

const lang = localStorage.getItem('lang');
const langMapping = langMappings[lang];
const langLabels = langMapping.labels;

function getGradeLabel(grade) {
  for (let key of langLabels) {
    if (grade >= key.grade) {
      if (grade > 7.0) {
        return 'N';
      }
      else if (grade > 6.0) {
        return 'B';
      }

      const gradeVal = grade > 5.0 ? 5.0 : grade;
      return `${gradeVal.toFixed(1)}${key.text}`;
    }
  }
};

grades.forEach((element) => {
  element.text = getGradeLabel(element.grade);
});

const peopleTotal = grades.reduce((partialSum, a) => partialSum + a.people, 0);
const attempts = grades.filter(x => x.grade < 6.0);
const gradesDisplay = localStorage.getItem('course-plot-absent') === 'false' ? attempts : grades;
const attemptsTotal = attempts.reduce((partialSum, a) => partialSum + a.people, 0);
const attemptsTotalGlobal = grades.filter(x => x.grade !== 6.0).reduce((partialSum, a) => partialSum + a.people, 0);
const failedAttempts = attempts.filter(x => x.grade > 4.0);
const failedAttemptsGlobal = grades.filter(x => (x.grade > 4.0 && x.grade < 7.0) || x.grade > 7.0);
const failedAttemptsTotal = failedAttempts.reduce((partialSum, a) => partialSum + a.people, 0);
const failedAttemptsGlobalTotal = failedAttemptsGlobal.reduce((partialSum, a) => partialSum + a.people, 0);
const gradeTotal = attempts.reduce((partialSum, a) => partialSum + a.people * a.grade, 0);
const passedAttempts = attempts.filter(x => x.grade <= 4.0);
const gradePassed = passedAttempts.reduce((partialSum, a) => partialSum + a.people * a.grade, 0);

const round = function(x, digits)
{
  const result = Number.parseFloat(x).toFixed(digits);
  return result.endsWith('0') ? Number.parseFloat(x).toFixed(digits - 1) : result;
}

const attemptsTotalSafe = attemptsTotal === 0 ? 1 : attemptsTotal;
const attemptsTotalGlobalSafe = attemptsTotalGlobal === 0 ? 1 : attemptsTotalGlobal;
const passedAttemptsSafe = (attemptsTotal - failedAttemptsTotal) === 0 ? 1 : (attemptsTotal - failedAttemptsTotal);

d3.select('#course-people-total').text(peopleTotal);
d3.select('#course-attempts-total').text(attemptsTotalGlobal);
d3.select('#course-failed-percent').text(`${round(failedAttemptsGlobalTotal / attemptsTotalGlobalSafe * 100, 2)}%`);
d3.select('#course-grade-avg').text(round(gradeTotal / attemptsTotalSafe, 2));
d3.select('#course-grade-avg-passed').text(round(gradePassed / passedAttemptsSafe, 2));

const barColor = function (d)
{
  const v = d.grade;
  if (v <= 4.0)
  {
    const hue = (4.0 - v) * 40.0;
    return `hsl(${hue}, 100%, 50%)`;
  }
  else if (v <= 5.0)
  {
    const hue = (5.0 - v) * 25.0 + 25.0;
    return `hsl(0, 100%, ${hue}%)`;
  }
  else if (v >= 8.0)
  {
    return 'hsl(0, 100%, 50%)';
  }
  else if (v >= 7.0)
  {
    return 'hsl(120, 100%, 50%)';
  }
  return 'hsl(0, 0%, 25%)';
};

const wrapper = document.querySelector('.wrapper');
const wrapperStyle = getComputedStyle(wrapper);
const plotWidth = parseInt(wrapperStyle['width']);
const plotHeight = Math.round(36.6 * (gradesDisplay.length + 1));
const plotContainer = document.getElementById('course-plot');
const plotMarginRight = 60.0;
const plotMarginLeft = langMapping.marginLeft;

function getGradePlotLegend(d) {
  const div = Math.min(d.people / attemptsTotalGlobalSafe, 1.0);
  const parts = round(div * 100.0, 2);
  return `${parts}% #${d.people}`;
}

const plot = Plot.plot({
  marks: [
    Plot.barX(gradesDisplay, {x: 'people', y: 'text', fill: barColor}),
    Plot.text(gradesDisplay, {
      x: 'people',
      y: 'text',
      text: getGradePlotLegend,
      fill: 'var(--minima-text-color)',
      dx: plotMarginRight / 2.0})
  ],
  height: plotHeight,
  width: plotWidth,
  marginRight: plotMarginRight,
  marginLeft: plotMarginLeft,
  y: { type: "band", label: langMapping.yLabel, line: true },
  x: { label: langMapping.xLabel, grid: true }
});

plotContainer.append(plot);

async function downloadImage(url, filename) {
  return await fetch(url, {
    mode : 'no-cors',
  })
  .then(response => response.blob())
  .then(blob => {
    let blobUrl = window.URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.download = filename;
    a.href = blobUrl;
    document.body.appendChild(a);
    a.click();
    a.remove();
    return blob;
  });
}

const preset = presets.offscreen();
preset.ignoreClear = true;

async function convertImage(data) {
  const {
    width,
    height,
    svg,
    type
  } = data;
  const canvas = new OffscreenCanvas(width, height);
  const ctx = canvas.getContext('2d');
  
  ctx.fillStyle = "#ffffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const v = await Canvg.from(ctx, svg, preset);

  // Render only first frame, ignoring animations and mouse.
  await v.render();

  const blob = await canvas.convertToBlob({ 'type': type });
  const pngUrl = URL.createObjectURL(blob);

  return pngUrl;
}

async function saveImage(mode, format) {
  const rootStyle = getComputedStyle(document.documentElement);
  const modes = {
    'light': 'lm-',
    'dark': 'dm-',
    'auto': ''
  };
  const rootBgColor = rootStyle.getPropertyValue(`--minima-${modes[mode]}background-color`);
  const rootTextColor = rootStyle.getPropertyValue(`--minima-${modes[mode]}text-color`);

  let svg = plotContainer.innerHTML;
  const textStart = svg.indexOf('<g aria-label="text"');
  const textEnd = svg.indexOf('</g>', textStart);
  svg = svg.replace('height: intrinsic;', `height: ${plotHeight};`);
  svg = svg.replace('<line aria-label="frame"', `<rect class="course-plot-bg" x="0" width="${plotWidth}" y="0" height="${plotHeight}" style="fill: ${rootBgColor};"></rect><line aria-label="frame"`);
  svg = svg.replace(/(?<=<text)[^>]*(?=>)/gm, ` style="fill: ${rootTextColor}" $&`);

  await convertImage({
    width: plotWidth + plotMarginRight,
    height: plotHeight + plotMarginRight / 2.0,
    svg: svg,
    type: `image/${format}`
  }).then((imageUrl) => downloadImage(imageUrl, `newplot.${format}`));
}

document.getElementById('course-plot-save-light').addEventListener('click', async (event) => await saveImage('light', 'png'));
document.getElementById('course-plot-save-dark').addEventListener('click', async (event) => await saveImage('dark', 'png'));

const langPicker = document.getElementById('course-plot-lang');
langPicker.value = lang;
langPicker.addEventListener('change', (event) => { localStorage.setItem('lang', event.target.value); location.reload(); });

document.getElementById('course-plot-absent').addEventListener('click', (event) => {
  localStorage.setItem('course-plot-absent', localStorage.getItem('course-plot-absent') === 'false' ? 'true' : 'false');
  location.reload();
});
