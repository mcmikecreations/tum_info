import {
  Canvg,
  presets
} from 'https://cdn.skypack.dev/canvg@^4.0.1'

const peopleTotal = grades.reduce((partialSum, a) => partialSum + a.people, 0);
const attempts = grades.filter(x => x.grade < 6.0);
const attemptsTotal = attempts.reduce((partialSum, a) => partialSum + a.people, 0);
const failedAttempts = attempts.filter(x => x.grade > 4.0);
const failedAttemptsTotal = failedAttempts.reduce((partialSum, a) => partialSum + a.people, 0);
const gradeTotal = attempts.reduce((partialSum, a) => partialSum + a.people * a.grade, 0);
const passedAttempts = attempts.filter(x => x.grade <= 4.0);
const gradePassed = passedAttempts.reduce((partialSum, a) => partialSum + a.people * a.grade, 0);

const round = function(x, digits)
{
  const pow = Math.pow(10, digits);
  return Math.round(x * pow) / pow;
}

d3.select('#course-people-total').text(peopleTotal);
d3.select('#course-attempts-total').text(attemptsTotal);
d3.select('#course-failed-percent').text(`${round(failedAttemptsTotal / attemptsTotal * 100, 2)}%`);
d3.select('#course-grade-avg').text(round(gradeTotal / attemptsTotal, 2));
d3.select('#course-grade-avg-passed').text(round(gradePassed / (attemptsTotal - failedAttemptsTotal), 2));

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
  return 'hsl(0, 0%, 25%)';
};

const wrapper = document.querySelector('.wrapper');
const wrapperStyle = getComputedStyle(wrapper);
const plotWidth = parseInt(wrapperStyle['width']);
const plotHeight = Math.round(36.6 * grades.length);
const plotContainer = document.getElementById('course-plot');
const plotMarginRight = 60.0;

const plot = Plot.plot({
  marks: [
    Plot.barX(grades, {x: 'people', y: 'grade', fill: barColor}),
    Plot.text(grades, {
      x: 'people',
      y: 'grade',
      text: d => `${round(d.people / attemptsTotal * 100.0, 2)}% #${d.people}`,
      fill: 'var(--minima-text-color)',
      dx: plotMarginRight / 2.0})
  ],
  height: plotHeight,
  width: plotWidth,
  marginRight: plotMarginRight,
  y: { line: true },
  x: { grid: true }
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
