import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { TeamCrest } from '../TeamCrest'

describe('TeamCrest', () => {
  it('renders the club crest from the FPL badge CDN, keyed by club code', () => {
    render(<TeamCrest code={43} team="Man City" teamShort="MCI" />)
    const img = screen.getByRole('img', { name: 'Man City crest' })
    expect(img).toHaveAttribute(
      'src',
      'https://resources.premierleague.com/premierleague/badges/70/t43.png',
    )
  })

  it('falls back to the short code when no crest code is available', () => {
    render(<TeamCrest code={0} team="Man City" teamShort="MCI" />)
    expect(screen.queryByRole('img')).not.toBeInTheDocument()
    expect(screen.getByText('MCI')).toBeInTheDocument()
  })

  it('renders nothing when there is no code and no short code to fall back to', () => {
    const { container } = render(<TeamCrest code={0} team="Man City" />)
    expect(container).toBeEmptyDOMElement()
  })
})
