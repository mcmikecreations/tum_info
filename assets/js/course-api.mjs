const courseApiUrl = 'https://mcmikecreations.github.io/tum_info/api/courses.json';

class Grade {
    constructor(data) {
        this.grade = data.grade;
        this.people = data.people;
    }
}

class Course {
    constructor(data) {
        this.school = data.school;
        this.code = data.code;
        this.semester = data.semester;
        this.examType = data.examType;
        this.name = data.name;
        this.date = new Date(data.date);
        this.ects = data.ects;
        this.hours = data.hours;
        this.mode = data.mode;
        this.lang = data.lang;
        this.peopleTotal = data.peopleTotal;
        this.peopleFailed = data.peopleFailed;
        this.attemptsTotal = data.attemptsTotal;
        this.attemptsFailedPercent = data.attemptsFailedPercent;
        this.averageTotal = data.averageTotal;
        this.averagePassed = data.averagePassed;
        this.grades = data.grades.map(grade => new Grade(grade));
    }

    school;
    code;
    semester;
    examType;
    name;
    date;
    ects;
    hours;
    mode;
    lang;
    peopleTotal;
    peopleFailed;
    attemptsTotal;
    attemptsFailedPercent;
    averageTotal;
    averagePassed;
    /**
     * One or more grade statistics for a course.
     * @type {Array<Grade>}
     */
    grades;

    /**
     * List of available courses.
     * @type {Array<Course> | undefined}
     */
    static courseList = undefined;
}

/**
 * 
 * @param {string} code uppercase course code, e.g., IN2386.
 * @param {string | undefined} semester uppercase semester of course start, e.g., 2023WS or 23WS.
 * @param {string | undefined} apiUrl URL to fetch course data from. Defaults to statically hosted website.
 * 
 * @returns {Promise<Array<Course>>} Zero or more courses that match the code and optionally semester.
 */
async function fetchCourse(code, semester, apiUrl) {
    if (apiUrl === undefined) {
        apiUrl = courseApiUrl;
    }

    if (Course.courseList === undefined) {
        try {
            const response = await fetch(apiUrl);
            Course.courseList = await response.json();
        }
        catch (error) {
            console.error('Error fetching course data:', error);
        }
    }

    if (Course.courseList !== undefined) {
        if (semester !== undefined) {
            if (semester.length === 4) semester = '20' + semester;
            return Course.courseList.filter(x => x.semester === semester && x.code === code);
        } else {
            return Course.courseList.filter(x => x.code === code);
        }
    }

    return [];
}

export {
    courseApiUrl,
    Grade,
    Course,
    fetchCourse,
};