let allPapers = [];
const allKeys = {
    authors: [],
    keywords: [],
    session: [],
    titles: [],
    all: [],
}
const filters = {
    authors: null,
    keywords: null,
    session: null,
    title: null,
    all: null,
};

let chairs = {};

let render_mode = 'compact';

const persistor = new Persistor('Mini-Conf-Papers');

const updateCards = (papers) => {
    const storedPapers = persistor.getAll();
    papers.forEach(
      openreview => {
          openreview.content.read = storedPapers[openreview.id] || false
      })

    const readCard = (iid, new_value) => {
        persistor.set(iid, new_value);
        // storedPapers[iid] = new_value ? 1 : null;
        // Cookies.set('papers-selected', storedPapers, {expires: 365});
    }

    const all_mounted_cards = d3.select('.cards')
      .selectAll('.myCard', openreview => openreview.id)
      .data(papers, d => d.number)
      .join('div')
      .attr('class', 'myCard col-xs-6 col-md-4')
      .html(card_html)

    all_mounted_cards.select('.card-title')
      .on('click', function (d) {
          const iid = d.id;
          all_mounted_cards.filter(d => d.id === iid)
            .select(".checkbox-paper").classed('selected', function () {
              const new_value = true;//!d3.select(this).classed('not-selected');
              readCard(iid, new_value);
              return new_value;
          })
      })

    all_mounted_cards.select(".checkbox-paper")
      .on('click', function (d) {
          const iid = d.id;
          const new_value = !d3.select(this).classed('selected');
          readCard(iid, new_value);
          d3.select(this).classed('selected', new_value)
      })


    lazyLoader();
}

/* Randomize array in-place using Durstenfeld shuffle algorithm */
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        const temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}

const render = () => {
    const f_test = [];

    updateSession();

    Object.keys(filters)
      .forEach(k => {filters[k] ? f_test.push([k, filters[k]]) : null})

    // console.log(f_test, filters, "--- f_test, filters");
    if (f_test.length === 0) updateCards(allPapers)
    else {
        const fList = allPapers.filter(
          d => {
              let i = 0, pass_test = true;
              while (i < f_test.length && pass_test) {
                  if (f_test[i][0] === 'titles') {
                      pass_test &= d.content['title'].toLowerCase()
                        .indexOf(f_test[i][1].toLowerCase()) > -1;

                  } else if (f_test[i][0] === 'all') {
                      let allstrings = d.content['authors'].join(" ") + d.content['keywords'].join(" ") + d.content['title'];
                      allstrings = allstrings.toLowerCase();
                      pass_test &= allstrings.indexOf(f_test[i][1].toLowerCase()) > -1;
                  } else {
                    pass_test &= d.content[f_test[i][0]].join(" ").toLowerCase().indexOf(
                      f_test[i][1].toLowerCase()) > -1
                  }
                  i++;
              }
              return pass_test;
          });
        // console.log(fList, "--- fList");
        updateCards(fList)
    }

}

const updateFilterSelectionBtn = value => {
    d3.selectAll('.filter_option label')
      .classed('active', function () {
          const v = d3.select(this).select('input').property('value')
          return v === value;
      })
}

const updateSession = () => {
    const urlSession = getUrlParameter("session");
    if (urlSession) {
        filters['session'] = urlSession;
        d3.select('#session_name').text(urlSession);
        d3.select('#session_chair').text(chairs[urlSession]);
        d3.select('#shuffle').style("visibility", "hidden");
        d3.select('.session_notice').classed('d-none', null);
        return true;
    } else {
        filters['session'] = null
        d3.select('#shuffle').style("visibility", "visible");
        return false;
    }
}

/**
 * START here and load JSON.
 */
const start = () => {
    const urlFilter = getUrlParameter("filter") || 'all';
    setQueryStringParameter("filter", urlFilter);
    updateFilterSelectionBtn(urlFilter)


    d3.json('serve_chairs.json').then(data => {
      for (d of data) {
        chairs[d['UID']] = d['chair'];
      }
    });

    d3.json('papers.json').then(papers => {
        // console.log(papers, "--- papers");

        // shuffleArray(papers);

        allPapers = papers;
        calcAllKeys(allPapers, allKeys);
        setTypeAhead(urlFilter,
          allKeys, filters, render);
        updateCards(allPapers)


        const urlSearch = getUrlParameter("search");
        if ((urlSearch !== '') || updateSession()) {
            filters[urlFilter] = urlSearch;
            $('.typeahead_all').val(urlSearch);
            render();
        }


    }).catch(e => console.error(e))
}


/**
 * EVENTS
 * **/

d3.selectAll('.filter_option input').on('click', function () {
    const me = d3.select(this)

    const filter_mode = me.property('value');
    setQueryStringParameter("filter", filter_mode);
    setQueryStringParameter("search", '');
    updateFilterSelectionBtn(filter_mode);


    setTypeAhead(filter_mode, allKeys, filters, render);
    render();
})

d3.selectAll('.remove_session').on('click', () => {
    setQueryStringParameter("session", '');
    render();

})

d3.selectAll('.render_option input').on('click', function () {
    const me = d3.select(this);
    render_mode = me.property('value');

    render();
})

d3.select('.reshuffle').on('click', () => {
    shuffleArray(allPapers);

    render();
})

/**
 * CARDS
 */

const keyword = kw => `<a href="papers.html?filter=keywords&search=${kw}"
                       class="text-secondary text-decoration-none">${kw.toLowerCase()}</a>`
const sessionurl = s => `<a href="papers.html?filter=keywords&session=${s}"
                        class="text-secondary text-decoration-none">${s}</a>`       

const card_image = (openreview, show) => {
    if (show) return ` <center><img class="lazy-load-img cards_img" data-src="https://iclr.github.io/iclr-images/small/${openreview.id}.jpg" width="80%"/></center>`
    else return ''
}

const card_detail = (openreview, show) => {
    if (show)
        return ` 
     <div class="pp-card-header-details">
        <p class="card-text"> ${openreview.content.TLDR ? openreview.content.TLDR : ''}</p>
        <p class="card-text"><span class="font-weight-bold">Subject areas:</span>
            ${openreview.content.keywords.map(keyword).join(', ')}
        </p>
        <p class="card-text"><span class="font-weight-bold">Presented in:</span>
            ${openreview.content.session.map(sessionurl).join(', ')}
        </p>
    </div>
`
    else return ''
}

const card_time_small = (openreview, show) => {
    const cnt = openreview.content;
    return show ? `
<!--    <div class="pp-card-footer">-->
    <div class="text-center" style="margin-top: 10px;">
    ${cnt.session.filter(s => s.match(/.*[0-9]/g)).map(
      (s, i) => `<a class="card-subtitle text-muted" href="?session=${encodeURIComponent(
        s)}">${s.replace('Session ', '')}</a> ${card_live(
        cnt.session_links[i])} ${card_cal(openreview, i)} `).join(', ')}
    </div>
<!--    </div>-->
    ` : '';
}

const card_icon_video = icon_video(16);
const card_icon_cal = icon_cal(16);

const card_live = (link) => `<a class="text-muted" href="${link}">${card_icon_video}</a>`
const card_cal = (openreview, i) => `<a class="text-muted" href="webcal://iclr.github.io/iclr-images/calendars/poster_${openreview.forum}.${i}.ics">${card_icon_cal}</a>`

// const card_time_detail = (openreview, show) => {
//     const cnt = openreview.content;
//     return show ? `
// <!--    <div class="pp-card-footer">-->
//     <div class="text-center text-monospace small" style="margin-top: 10px;">
//     ${cnt.session.filter(s => s.match(/.*[0-9]/g))
//       .map((s, i) => `${s} ${cnt.session_times[i]} ${card_live(cnt.session_links[i])}   `)
//       .join('<br>')}
//     </div>
// <!--    </div>-->
//     ` : '';
// }

//language=HTML
const card_html = openreview => `
        <div class="pp-card pp-mode-` + render_mode + ` ">
            <div class="pp-card-header">
            <div class="checkbox-paper ${openreview.content.read ? 'selected' : ''}" style="display: block;position: absolute; bottom:35px;left: 35px; visibility: hidden;">✓</div>            
                <a href="papers/paper_${openreview.id}.html"
                   class="text-muted">
                   <h5 class="card-title" align="center" ${openreview.content.read ? 'style="color:#2294e0;"' : ''}> ${position_selector(openreview)} ${openreview.content.title} </h5></a>
                <h6 class="card-subtitle text-muted" align="center">
                        ${openreview.content.authors.join(', ')}
                </h6>
                ${zoom_selector(openreview)}
            </div>
               
                ${card_detail(openreview, (render_mode === 'detail'))}
        </div>`

const zoom_selector = (openreview) => {
  if (openreview.id.includes("OP")) return '';
  const urlSession = getUrlParameter("session");
  const zoom_links = openreview.content.zoom;
  const sessions = openreview.content.session;
  let link = ''
  if (urlSession === sessions[0]) link = zoom_links[0];
  if (urlSession === sessions[1]) link = zoom_links[1];
  if (!(link === ''))
    return '<br /><h6 class="card-subtitle" align="center"> <a href="' + link + '" target="_blank">[Zoom link for poster session]</a></h6>';
  else
    return '';
};

const position_selector = (openreview) => {
  const urlSession = getUrlParameter("session");
  const positions = openreview.content.positions;
  const sessions = openreview.content.session;
  let position = ''
  if (urlSession === sessions[0]) position = positions[0];
  if (urlSession === sessions[1]) position = positions[1];
  if (!(position === ''))
    return '' + position + '.';
  else
    return '';
};
